# parking_system/core.py
import time
from datetime import datetime
from parking_system.utils import (
    init_camera, capture_frame,
    init_serial, read_serial_line,
    init_ocr, read_plate_text,
    load_roi, save_parking_log
)

class ParkingSystem:
    def __init__(self, serial_port="COM3", baud_rate=9600, camera_index=1, price_per_min=2.0):
        self.serial = init_serial(serial_port, baud_rate)
        self.camera = init_camera(camera_index)
        self.reader = init_ocr()
        self.roi = load_roi("roi_coordinates.json")
        self.price_per_min = price_per_min
        self.parking_log = {}
        print("[SYSTEM] Waiting for Arduino response...")

    def capture_and_recognize(self):
        """Capture image and recognize license plate text."""
        frame = capture_frame(self.camera)
        if frame is None:
            print("[ERROR] No frame captured.")
            return None

        x, y, w, h = self.roi["x"], self.roi["y"], self.roi["w"], self.roi["h"]
        cropped = frame[y:y+h, x:x+w]
        plate = read_plate_text(self.reader, cropped)
        return plate

    def calculate_charge(self, entry_time, exit_time):
        duration = (exit_time - entry_time).total_seconds() / 60
        cost = duration * self.price_per_min
        return round(duration, 2), round(cost, 2)

    def process_serial_input(self):
        """Handle Arduino ENTRY/EXIT messages."""
        line = read_serial_line(self.serial)
        if not line:
            return None

        if line == "ENTRY":
            print("\n[ENTRY DETECTED] Capturing plate...")
            plate = self.capture_and_recognize()
            if plate:
                self.parking_log[plate] = datetime.now()
                print(f"[INFO] Car {plate} entered at {self.parking_log[plate].strftime('%H:%M:%S')}")
            else:
                print("[WARN] No plate detected.")

        elif line == "EXIT":
            print("\n[EXIT DETECTED] Capturing plate...")
            plate = self.capture_and_recognize()
            if plate and plate in self.parking_log:
                entry_time = self.parking_log[plate]
                exit_time = datetime.now()
                duration, cost = self.calculate_charge(entry_time, exit_time)
                save_parking_log(plate, entry_time, exit_time, duration, cost)
                print(f"[INFO] Car {plate} parked for {duration} min | Charge ₹{cost}")
                del self.parking_log[plate]
            else:
                print("[WARN] Exit detected but no matching entry found.")

    def cleanup(self):
        print("[SYSTEM] Releasing resources...")
        if self.camera:
            self.camera.release()
        if self.serial:
            self.serial.close()
        print("[SYSTEM] Clean exit.")
