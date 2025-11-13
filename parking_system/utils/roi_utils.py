# parking_system/utils/roi_utils.py
import json
import os

def load_roi(filepath="roi_coordinates.json"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"[ERROR] ROI file not found: {filepath}")
    with open(filepath, "r") as f:
        data = json.load(f)
    print(f"[ROI] Loaded ROI: x={data['x']} y={data['y']} w={data['w']} h={data['h']}")
    return data
