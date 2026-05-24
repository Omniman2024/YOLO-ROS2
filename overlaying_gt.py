import glob
import cv2
import os
from tqdm import tqdm

BASE_IMG_DIR = "/mnt/c/Users/anubh/OneDrive/Desktop/CSDD_resized/img" # Replace with local path to the img subfolder within the dataset folder
BASE_MASK_DIR = "/mnt/c/Users/anubh/OneDrive/Desktop/CSDD_resized/ground_truth" # Replace with the local path to the ground_truth subfolder within the dataset folder
BASE_LABEL_DIR = "/mnt/c/Users/anubh/OneDrive/Desktop/CSDD_resized/labels" # Replace with the local path to the labels folder
OUTPUT_BASE = "/mnt/c/Users/anubh/OneDrive/Desktop/Labeled_GT_All" # Replace with the path to the output 
SPLITS = ["train", "val", "test"]
CLASSES = {0: 'Scratch', 1: 'Spot', 2: 'Rust'}

for split in SPLITS:
    print(f"\nProcessing {split} set...")

    img_dir = os.path.join(BASE_IMG_DIR, split)
    mask_dir = os.path.join(BASE_MASK_DIR, split)
    label_dir = os.path.join(BASE_LABEL_DIR, split)
    output_dir = os.path.join(OUTPUT_BASE, split)

    os.makedirs(output_dir, exist_ok=True)
    image_paths = glob.glob(os.path.join(img_dir, "*.jpg"))

    for img_path in tqdm(image_paths):
        img_id = os.path.splitext(os.path.basename(img_path))[0]
        mask_path = os.path.join(mask_dir, f"{img_id}_mask.png")
        label_path = os.path.join(label_dir, f"{img_id}.txt")
        image = cv2.imread(img_path)
        if image is None:
            continue
        h, w = image.shape[:2]
        if os.path.exists(mask_path):
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            mask = cv2.resize(mask, (w, h))
            overlay = image.copy()
            overlay[mask > 0] = [0, 255, 0]
            image = cv2.addWeighted(overlay, 0.3, image, 0.7, 0)
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    cls, x, y, nw, nh = map(float, line.split()[:5])
                    # YOLO specific coordinates
                    x1 = int((x - nw/2) * w)
                    y1 = int((y - nh/2) * h)
                    label = CLASSES.get(int(cls), "Unknown")
                    cv2.putText(image, f"GT: {label}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4)
                    cv2.putText(image, f"GT: {label}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        save_path = os.path.join(output_dir, f"{img_id}_Labeled_GT.jpg")
        cv2.imwrite(save_path, image)

    print(f"Done: {split} → saved in {output_dir}")

print("\nAll datasets processed successfully!")