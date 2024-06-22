import argparse
import requests
import re
import time
import zipfile
import os
import yaml
from pathlib import Path
import shutil

UNZIP_DIR_PREFIX = "extracted_"
DATA_YAML_FILE = 'data.yaml'

def get_filename_from_cd(cd):
    ## https://www.codementor.io/@aviaryan/downloading-files-from-urls-in-python-77q3bs0un
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def download_dataset(url, output):
    print("Download URI:", url)
    r = requests.get(url, allow_redirects=True)
    filename = get_filename_from_cd(r.headers.get('content-disposition')) if output == "" else output
    print("Downloading to file:", filename)
    open(filename, 'wb').write(r.content)
    print("Done dowloading")

def re_label(dir_path, custom_classes_matching):
    # dir_basename = os.path.basename(os.path.normpath(dir_path))
    base_dir = Path(dir_path)
    if not base_dir.exists() or not base_dir.is_dir():
        raise ValueError(f"The path {dir_path} does not exist or is not a directory.")
    parent_dir = base_dir.parent
    # Rename the last folder in the path
    new_folder_name = base_dir.stem + "_source"
    source_base_dir = parent_dir / new_folder_name
    shutil.copytree(base_dir, source_base_dir)

    maxClassID = max(custom_classes_matching.values())
    undefined_class_id = maxClassID + 1
    for label_file in source_base_dir.iterdir():
        with open(label_file) as _f:
            boxes = _f.readlines()
            newboxes = []
            for box in boxes:
                yolo_annotation = box.rstrip('\r\n').split(" ")
                class_id = int(yolo_annotation[0])
                if class_id not in custom_classes_matching:
                    print("Class {} not found in custom classes matching. Using max ID: {}. File: '{}'".format(class_id, undefined_class_id, label_file))
                class_id_new = custom_classes_matching[class_id] if class_id in custom_classes_matching else undefined_class_id
                if class_id_new < 0:
                    print("bad class id", label_file)
                yolo_annotation[0] = "{}".format(class_id_new)
                newboxes.append(" ".join(yolo_annotation))
            newfname = base_dir / label_file.name
            with open(newfname, 'w') as _newf:
                contents = "\n".join(newboxes)
                _newf.writelines(contents)

class DatasetDownloader():
    url_template = 'https://universe.roboflow.com/ds/{}?key={}'
    dataset_classes = {}
    custom_classes = {}
    custom_classes_matching = {}
    def __init__(self, dataset_id, key, custom_classes = {}, custom_classes_matching = {}):
        self.dataset_id = dataset_id
        self.key = key
        self.output_filename = ""
        self.custom_classes = custom_classes
        self.custom_classes_matching = custom_classes_matching

    def download(self, output_filename = ""):
        st = time.time()
        url = self.url_template.format(self.dataset_id, self.key)
        print("Start downloading dataset with ID '{}'...".format(self.dataset_id))
        r = requests.get(url, allow_redirects=True)
        filename = get_filename_from_cd(r.headers.get('content-disposition')) if output_filename == "" else output_filename
        self.output_filename = filename
        print("\tOutput filename: '{}'".format(self.output_filename))
        open(self.output_filename, 'wb').write(r.content)
        print("\t...Done downloading. Elapsed: {}".format(time.time() - st))
    
    def unzip(self):
        with zipfile.ZipFile(self.output_filename,"r") as zip_ref:
            zip_ref.extractall(UNZIP_DIR_PREFIX + os.path.splitext(self.output_filename)[0])

    def extract_dataset_classes(self):
        directory = UNZIP_DIR_PREFIX + os.path.splitext(self.output_filename)[0]
        data_file = directory + '/' + DATA_YAML_FILE
        print("Datafile is: '{}'".format(data_file))
        with open(data_file, 'r') as file:
            file_content = yaml.safe_load(file)
            classnames = file_content['names']
            for id, classname in enumerate(classnames):
                self.dataset_classes[classname] = id
        print("Dataset classes:", self.dataset_classes)
        
    def download_and_prepare(self, output_filename = ""):
        self.download(output_filename=output_filename)
        self.unzip()
        self.extract_dataset_classes()
        if len(self.custom_classes) == 0 or self.custom_classes_matching == 0:
            return
        directory = UNZIP_DIR_PREFIX + os.path.splitext(self.output_filename)[0]
        train_labels_dir = directory + "/train/labels"
        test_labels_dir = directory + "/test/labels"
        val_labels_dir = directory + "/valid/labels"
        if os.path.isdir(train_labels_dir):
            print("Re-labeling annotations files in '{}' sub-directory".format(train_labels_dir))
            re_label(train_labels_dir, self.custom_classes_matching)
        if os.path.isdir(test_labels_dir):
            print("Re-labeling annotations files in '{}' sub-directory".format(test_labels_dir))
            re_label(test_labels_dir, self.custom_classes_matching)
        if os.path.isdir(val_labels_dir):
            print("Re-labeling annotations files in '{}' sub-directory".format(val_labels_dir))
            re_label(val_labels_dir, self.custom_classes_matching)

def main(args):
    custom_classes = {
        "severe_accident": 0,
        "moderate_accident": 1
    }
    # Dataset class ID <-> Custom class ID 
    custom_classes_matching = {
        0: 1,
        1: 0
    }
    dataset = DatasetDownloader(args.dataset_id, args.key, custom_classes=custom_classes, custom_classes_matching=custom_classes_matching)
    dataset.download_and_prepare(output_filename=args.output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Roboflow dataset downloader. Provide dataset ID, secret key and filename for dataset archive')
    parser.add_argument('--dataset_id', type=str, help='Dataset ID')
    parser.add_argument('--key', type=str, help='Secret key to download dataset. Do not share it with anyone beyound you or your team')
    parser.add_argument('--output', type=str, help='Save path for dataset archive (e.g. "my_dataset.zip"). It will be unzipped to folder with "extracted_" prefix', default='training_dataset.zip')
    args = parser.parse_args()
    main(args)

