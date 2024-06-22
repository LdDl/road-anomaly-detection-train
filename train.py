import argparse
from ultralytics import YOLO

valid_models_sizes = {'n', 's', 'm', 'l', 'x'}

def main(args):
    model_size = args.model_size.lower()
    if model_size not in valid_models_sizes:
        raise ValueError(f"Model size '{model_size}' is not recognized. Use 'n', 's', 'm', 'l' or 'x'")
    model = YOLO(f'yolov8{model_size}.yaml')
    print(args.cache_images)
    model.train(data=f'{args.yaml_path}/data.yaml', cache=args.cache_images, imgsz=args.image_size, batch=args.batch_size, epochs=args.epochs)
    model.export(format="onnx", opset=12, batch=1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to train YOLOv8 for given model parameters')
    parser.add_argument('--model_size', type=str, help='Model size. Possible values: n - for nano, s - small, m - medium, l - large, x - extra large', default='n')
    parser.add_argument('--image_size', type=str, help='Size of image. Image will be resized to {image_size}x{image_size}', default=608)
    parser.add_argument('--yaml_path', type=str, help='Path where is "data.yaml" file is located (e.g. "extracted_dataset"). Path should not contain filename itself')
    parser.add_argument('--batch_size', type=int, help='Batch size for training. Use "-1" if you want to utilize 60% of GPU memory', default=8)
    parser.add_argument('--epochs', type=int, help='Number of epochs', default=100)
    parser.add_argument('--cache_images', type=bool, help='Caching images. If enabled than more RAM will be consumed but training process will be faster', default=False)
    args = parser.parse_args()
    main(args)

