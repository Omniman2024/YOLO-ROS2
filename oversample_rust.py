import os
import shutil
import glob
from tqdm import tqdm

BASE_DIR = "/mnt/c/Users/anubh/OneDrive/Desktop/CSDD_resized"
TRAIN_IMG = os.path.join(BASE_DIR, "img/train")
TRAIN_LBL = os.path.join(BASE_DIR, "labels/train")

def clean_old_copies():
    print(" Cleaning up old oversampled copies...")
    img_copies = glob.glob(os.path.join(TRAIN_IMG, "rust_copy_*"))
    for f in img_copies:
        os.remove(f)
    lbl_copies = glob.glob(os.path.join(TRAIN_LBL, "rust_copy_*"))
    for f in lbl_copies:
        os.remove(f)    
    print(f" Removed {len(img_copies)} old image copies and {len(lbl_copies)} old label copies.")

def oversample_rust(factor=1):
    clean_old_copies()
    label_files = [f for f in os.listdir(TRAIN_LBL) if f.endswith('.txt') and not f.startswith('rust_copy_')]
    rust_count = 0
    print(f" Scanning for original Rust (Class 2) to oversample by {factor}x...")
    for lbl_file in tqdm(label_files):
        lbl_path = os.path.join(TRAIN_LBL, lbl_file)
        has_rust = False
        with open(lbl_path, 'r') as f:
            for line in f:
                if line.startswith('2 '): 
                    has_rust = True
                    break
        if has_rust:
            rust_count += 1
            img_file = lbl_file.replace('.txt', '.jpg')
            for i in range(1, factor):
                new_img_name = f"rust_copy_{i}_{img_file}"
                new_lbl_name = f"rust_copy_{i}_{lbl_file}"
                shutil.copy2(os.path.join(TRAIN_IMG, img_file), 
                             os.path.join(TRAIN_IMG, new_img_name))
                shutil.copy2(os.path.join(TRAIN_LBL, lbl_file), 
                             os.path.join(TRAIN_LBL, new_lbl_name))

    print(f" Oversampling complete! Multiplied {rust_count} Rust images by {factor}.")
    print(f" Total training images now: {len(os.listdir(TRAIN_IMG))}")

if __name__ == "__main__":
    oversample_rust(factor=1)