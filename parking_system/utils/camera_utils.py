# parking_system/utils/camera_utils.py
import cv2
import os
import time

SNAPSHOT_FOLDER = "snapshots"
if not os.path.exists(SNAPSHOT_FOLDER):
    os.makedirs(SNAPSHOT_FOLDER)

def init_camera(index=1):
    cam = cv2.VideoCapture(index)
    if not cam.isOpened():
        raise RuntimeError(f"[ERROR] Could not open camera at index {index}")
    print(f"[CAMERA] Initialized camera index {index}")
    return cam

def capture_frame(camera):
    time.sleep(0.5)
    ret, frame = camera.read()
    if not ret:
        print("[ERROR] Failed to capture frame")
        return None
    filename = os.path.join(SNAPSHOT_FOLDER, f"snapshot_{int(time.time())}.jpg")
    cv2.imwrite(filename, frame)
    print(f"[INFO] Snapshot saved: {filename}")
    return frame
