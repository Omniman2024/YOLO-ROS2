import torch
import cv2
import os

WEIGHTS_PATH = "/mnt/c/Users/anubh/OneDrive/Desktop/ME-222 Course Project/best.pt" # Replace with local path to the best.pt file created after running the YOLOv5 model
IMAGE_PATH = "/mnt/c/Users/anubh/OneDrive/Desktop/CSDD_Resized/img/train/0771.jpg" # Replace with local path to the image you want to test
OUTPUT_DIR = "/mnt/c/Users/anubh/OneDrive/Desktop/inference_output" # Replace with the output path
CONF_THRESH = 0.25
CLASS_NAMES = ['Scratch', 'Spot', 'Rust']

os.makedirs(OUTPUT_DIR, exist_ok=True)
print("Loading model...")
model = torch.hub.load(
    "/mnt/c/Users/anubh/OneDrive/Desktop/ME-222 Course Project/yolov5", # Replace with the local path to the yolov5 folder created after running the model
    'custom',
    path=WEIGHTS_PATH,
    source='local'
)

model.conf = CONF_THRESH
print("Running inference...")
results = model(IMAGE_PATH)

print("\nDetections:")
print(results.pandas().xyxy[0])

results.render()  
output_path = os.path.join(
    OUTPUT_DIR,
    "prediction_" + os.path.basename(IMAGE_PATH)
)
cv2.imwrite(output_path, results.ims[0])
print(f"\nPrediction saved at:\n{output_path}")