# roi_selector.py
import cv2
import json
import sys

CAMERA_INDEX = 1
ROI_FILE = "roi_coordinates.json"

cap = cv2.VideoCapture(CAMERA_INDEX)
ret, frame = cap.read()
if not ret:
    print("❌ Camera not detected. Close other camera apps and try again.")
    cap.release()
    sys.exit(1)

print("Draw ROI rectangle and press ENTER/SPACE to confirm, ESC to cancel.")
roi = cv2.selectROI("Select ROI", frame, False)
cv2.destroyAllWindows()
cap.release()

if roi == (0,0,0,0):
    print("No ROI selected. Exiting.")
    sys.exit(1)

x, y, w, h = roi
data = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
with open(ROI_FILE, "w") as f:
    json.dump(data, f)
print(f"✅ ROI saved to {ROI_FILE}: {data}")
