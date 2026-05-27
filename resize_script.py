import os 
from PIL import Image 

input_base = "/mnt/c/Users/anubh/OneDrive/Desktop/CSDD_seg" # Replace with input path (dataset folder)
output_base = "/mnt/c/Users/anubh/OneDrive/Desktop/CSDD_resized" # Replace with output path
target_size = (1024, 1024) 

def resize_dataset(subfolder, is_mask=False): 
    in_path = os.path.join(input_base, subfolder) 
    out_path = os.path.join(output_base, subfolder) 
    if not os.path.exists(out_path): os.makedirs(out_path) 
    for filename in os.listdir(in_path): 
        if filename.endswith((".jpg", ".png")): 
            img = Image.open(os.path.join(in_path, filename)) 
            resample_mode = Image.NEAREST if is_mask else Image.LANCZOS # Different resampling modes are used for mask and normal image.
            img_resized = img.resize(target_size, resample=resample_mode) 
            img_resized.save(os.path.join(out_path, filename)) 
    print(f"Finished resizing {subfolder}") 
    
resize_dataset("img/train", is_mask=False) 
resize_dataset("ground_truth/train", is_mask=True) 
resize_dataset("img/test", is_mask=False) 
resize_dataset("ground_truth/test", is_mask=True) 
resize_dataset("img/val", is_mask=False) 
resize_dataset("ground_truth/val", is_mask=True)