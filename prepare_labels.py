import os
import cv2
import numpy as np
from tqdm import tqdm

IN_BASE = "/mnt/c/Users/anubh/OneDrive/Desktop/CSDD_resized" # Replace with input path (dataset folder)
OUT_BASE = "/mnt/c/Users/anubh/OneDrive/Desktop/CSDD_resized/labels" # Replace with output path (where you want the labels folder to be created)

for s in ['train', 'val', 'test']:
    os.makedirs(f'{OUT_BASE}/{s}', exist_ok=True)


def prepare_yolo_labels(split):
    img_in = f'{IN_BASE}/img/{split}'          
    mask_in = f'{IN_BASE}/ground_truth/{split}'  
    img_files = [f for f in os.listdir(img_in) if f.endswith('.jpg')]
    for img_name in tqdm(img_files, desc=f"Processing {split}"):
        mask_name = img_name.replace('.jpg', '_mask.png')
        mask_path = os.path.join(mask_in, mask_name)
        if not os.path.exists(mask_path):
            continue
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        h, w = mask.shape 
        yolo_labels = []
        for class_id in [1, 2, 3]:
            binary_mask = np.uint8(mask == class_id)
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                x, y, bw, bh = cv2.boundingRect(cnt)
                # Convert to YOLO format (normalized)
                x_center = (x + bw / 2) / w
                y_center = (y + bh / 2) / h
                width = bw / w
                height = bh / h
                yolo_labels.append(f"{class_id - 1} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

        label_path = f"{OUT_BASE}/{split}/{img_name.replace('.jpg', '.txt')}"
        with open(label_path, 'w') as f:
            f.write("\n".join(yolo_labels))


for s in ['train', 'val', 'test']:
    prepare_yolo_labels(s)

print(f"YOLO label files saved at: {OUT_BASE}")