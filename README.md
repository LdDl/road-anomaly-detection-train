# Training objected detector for road accidents detection

## Table of Contents
- [About](#about)
- [Usage](#usage)
- [References](#references)

## About
It is just bunch of scripts to train road accidents detector for my pet-project written in Rust programming languages: https://github.com/LdDl/road-anomaly-detection

There are two scripts in this repository:
- `download.py` to download dataset of interest;
- `train.py` to run training process; (w.i.p)

## Usage
* Install dependencies
  ```shell
  pip3 install -r requirements.txt
  ```

* Navigate to selected dataset. In this case the link is:
  ```
  https://universe.roboflow.com/accident-detection-ffdrf/accident-detection-8dvh5
  ```

* Get dataset ID and unique key to download it.

* Run `download.py` script
  ```shell
  export DATASET_ID=YOUR-DATASET-ID
  export ROBOFLOW_KEY=YOUR-ACCOUNT-KEY
  
  python3 download.py --dataset_id $DATASET_ID --key $ROBOFLOW_KEY --output dataset.zip
  ```

  You can adjust classes if you need to in lines [119](download.py#L119) and [124](download.py#L124):
    - Undefined classes would be marked as (max class ID + 1).
    - Warning: Re-labeled annotations would be stored in `/train/labels`, `/test/labels` and `/valid/labels`. Source labels would be stored in `/train/labels_source`, `/test/labels_source` and `/valid/labels_source` respectively.


* Run `train.py` script
  ```shell
  python3 main.py
  ```
 
  @w.i.p

## References
* Developers of YOLOv8 - https://github.com/ultralytics/ultralytics. If you are aware of some original papers for YOLOv8 architecture, please contact me to mention it in this README.
* Dataset source https://universe.roboflow.com/accident-detection-ffdrf/accident-detection-8dvh5
