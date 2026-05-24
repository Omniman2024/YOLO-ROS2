import os
import glob
import cv2
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm

BASE_PATH = "/mnt/c/Users/anubh/OneDrive/Desktop/CSDD_resized" # Replace with local path to the dataset folder
WEIGHTS_PATH = "/mnt/c/Users/anubh/OneDrive/Desktop/best.pt" # Replace with the local path to the best.pt file created after running the YOLOv5 model
OUTPUT_DIR = "/mnt/c/Users/anubh/OneDrive/Desktop/analysis" # Replace with the output path

class CSDDMasterAuditor:
    def __init__(self, weights=WEIGHTS_PATH, img_dir=f"{BASE_PATH}/img/test", mask_dir=f"{BASE_PATH}/ground_truth/test"):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=weights, source='github', force_reload=False).to(self.device)
        self.model.conf = 0.25 
        self.img_dir = img_dir
        self.mask_dir = mask_dir
        self.classes = {0: 'Scratch', 1: 'Spot', 2: 'Rust'}
        self.stats = {i: {'inter': 0, 'union': 0, 'conf_scores': []} for i in self.classes.keys()}
        self.audit_records = []
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def run_audit(self):
        test_images = glob.glob(os.path.join(self.img_dir, "*.jpg"))
        print(f" Starting Master Audit on {len(test_images)} test images...")
        for img_path in tqdm(test_images):
            img_id = os.path.splitext(os.path.basename(img_path))[0]
            mask_path = os.path.join(self.mask_dir, f"{img_id}_mask.png")
            results = self.model(img_path)
            preds = results.xyxy[0].cpu().numpy() 
            
            # Metrics Logic (IoU)
            if os.path.exists(mask_path):
                self._compute_metrics(mask_path, preds)
            self.audit_records.append({
                'id': img_id,
                'path': img_path,
                'avg_conf': preds[:, 4].mean() if len(preds) > 0 else 0,
                'results': results
            })
        self._finalize_results()

    def _compute_metrics(self, mask_path, preds):
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        h, w = mask.shape 
        for cls_id in self.classes.keys():
            gt_cls = (mask == (cls_id + 1)).astype(np.uint8)
            pred_mask = np.zeros((h, w), dtype=np.uint8)
            for p in preds:
                if int(p[5]) == cls_id:
                    cv2.rectangle(pred_mask, (int(p[0]), int(p[1])), (int(p[2]), int(p[3])), 1, -1)
            self.stats[cls_id]['inter'] += np.logical_and(gt_cls, pred_mask).sum()
            self.stats[cls_id]['union'] += np.logical_or(gt_cls, pred_mask).sum()
            class_confs = [p[4] for p in preds if int(p[5]) == cls_id]
            self.stats[cls_id]['conf_scores'].extend(class_confs)

    def _finalize_results(self):
        # Generate Table
        summary = []
        for cid, name in self.classes.items():
            s = self.stats[cid]
            miou = (s['inter'] / s['union'] * 100) if s['union'] > 0 else 0
            avg_c = np.mean(s['conf_scores']) if s['conf_scores'] else 0
            summary.append({"Type": name, "mIoU (%)": round(miou, 2), "Avg Conf": round(avg_c, 3)})
        
        print("\n" + "="*50 + "\n" + pd.DataFrame(summary).to_string(index=False) + "\n" + "="*50)
        
        # Save Visual Artifacts (Best 5 / Worst 5)
        self.audit_records.sort(key=lambda x: x['avg_conf'], reverse=True)
        for i, record in enumerate(self.audit_records[:5] + self.audit_records[-5:]):
            label = "Best" if i < 5 else "Worst"
            img = record['results'].render()[0]
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            mask_path = os.path.join(self.mask_dir, f"{record['id']}_mask.png")
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            contours, _ = cv2.findContours((mask > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img, contours, -1, (0, 255, 0), 3) 
            cv2.imwrite(f"{OUTPUT_DIR}/{label}_{record['id']}_audit.jpg", img)

if __name__ == "__main__":
    auditor = CSDDMasterAuditor()
    auditor.run_audit()