import os
import yaml

DEFAULT_BASE = "/mnt/c/Users/anubh/OneDrive/Desktop"  
DEFAULT_DATASET = "/mnt/c/Users/anubh/OneDrive/Desktop/CSDD_resized"

def generate_yolo_configs(cls_pw, obj_pw, base_path=DEFAULT_BASE, dataset_path=DEFAULT_DATASET):
    data_config = {
        'path': dataset_path,     
        'train': 'img/train',
        'val': 'img/val',
        'test': 'img/test',
        'nc': 3,
        'names': ['Scratch', 'Spot', 'Rust']
    }

    data_yaml_path = os.path.join(base_path, "csdd.yaml")
    os.makedirs(os.path.dirname(data_yaml_path), exist_ok=True)
    with open(data_yaml_path, 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False)
        hyp_sim_config = {
            'lr0': 0.01, 
            'lrf': 0.01, 
            'momentum': 0.937, 
            'weight_decay': 0.0005,
            'warmup_epochs': 3.0, 
            'warmup_momentum': 0.8, 
            'warmup_bias_lr': 0.1,
            'box': 0.05, 
            'cls': 0.5, 
            'cls_pw': cls_pw,   
            'obj': 1.5, 
            'obj_pw': obj_pw,   
            'iou_t': 0.20, 
            'anchor_t': 4.0, 
            'fl_gamma': 0.0,
            'hsv_h': 0.015, 
            'hsv_s': 0.7, 
            'hsv_v': 0.6,
            'degrees': 0.0, 
            'translate': 0.1, 
            'scale': 0.5, 
            'shear': 0.0, 
            'perspective': 0.0,
            'flipud': 0.0, 
            'fliplr': 0.5, 
            'mosaic': 1.0, 
            'mixup': 0.0, 
            'copy_paste': 0.0,
            'blur': 0.15, 
            'median_blur': 0.1
        }
    hyp_yaml_path = os.path.join(base_path, "hyp.simulation.yaml")
    with open(hyp_yaml_path, 'w') as f:
        yaml.dump(hyp_sim_config, f)
    print(f" CONFIGS GENERATED (cls_pw: {cls_pw}, obj_pw: {obj_pw})")
    print(f" Data YAML: {data_yaml_path}")
    print(f" Hyp YAML:  {hyp_yaml_path}")

if __name__ == "__main__":
    generate_yolo_configs(cls_pw=1.0, obj_pw=1.0) # change these parameters to play around with the weighted loss parameters 