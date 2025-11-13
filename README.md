# 🚗 Car Parking System

An advanced automated parking management system that detects vehicle entry/exit, recognizes license plates using OCR, calculates parking charges in real-time, and provides a modern GUI for management.

## Features

- **🚙 Vehicle Detection**: IR sensors detect car entry and exit
- **📸 License Plate Recognition**: Automatic OCR-based plate detection
- **💰 Real-time Charge Calculation**: Automatic billing based on parking duration
- **🎛️ Arduino Integration**: Servo-controlled gate and LCD display
- **📊 Live Dashboard**: Modern GUI with real-time video feed and logs
- **📝 Parking Logs**: CSV-based transaction history

## System Architecture

### Hardware Components
- **Arduino Microcontroller**: Controls gate, sensors, and LCD display
- **IR Sensors**: Detect vehicle presence (entry, exit, slot occupancy)
- **Servo Motor**: Controls parking gate
- **20x4 LCD Display**: Shows parking status and slot information
- **USB Webcam**: Captures license plate images

### Software Stack
- **Backend**: Python with OpenCV, EasyOCR, PySerial
- **GUI**: Tkinter with modern dark theme
- **Firmware**: Arduino C++ (servo control, IR sensor reading)
- **Logging**: CSV-based transaction records

## Prerequisites

### System Requirements
- Windows/Linux/macOS with Python 3.8+
- Arduino board (Uno/Mega recommended)
- USB webcam (camera index 1)
- USB cable for Arduino connection

### Python Dependencies
```bash
pip install opencv-python
pip install easyocr
pip install pyserial
pip install pillow
pip install pandas
```

### Arduino Libraries
- `Servo.h` (built-in)
- `Wire.h` (built-in)
- `LiquidCrystal_I2C.h` (install via Arduino IDE)

## Installation & Setup

### 1. Clone/Download the Repository
```bash
git clone <repository-url>
cd CarParkingSystem
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Upload Arduino Firmware
1. Open [arduino_code.ino](arduino_code.ino) in Arduino IDE
2. Select your board type and COM port
3. Click **Upload**
4. Verify serial output shows initialization

### 4. Configure ROI (Region of Interest) for License Plate
Before running, you need to define the area where license plates appear in your camera feed:

```bash
python roi_selector.py
```

- This opens your camera feed
- Draw a rectangle around the license plate area
- Press **ENTER/SPACE** to confirm
- ROI coordinates are saved to `roi_coordinates.json`

**Alternative**: Edit [roi_coordinates.json](roi_coordinates.json) manually with known coordinates:
```json
{"x": 128, "y": 93, "w": 512, "h": 387}
```

### 5. Configure Serial Connection
Edit [main.py](main.py) or [parking_system/core.py](parking_system/core.py) to match your Arduino COM port:
```python
system = ParkingSystem(serial_port="COM3", baud_rate=9600, camera_index=1, price_per_min=2.0)
```

- **serial_port**: COM port where Arduino is connected (COM3, COM4, etc.)
- **camera_index**: Webcam index (usually 1 for secondary camera)
- **price_per_min**: Parking rate in ₹ per minute

## Running the System

### Start the Application
```bash
python main.py
```

This launches the **Parking Management System GUI** which:
- Displays live camera feed with vehicle detection
- Shows real-time parking slot availability
- Logs all vehicle entry/exit transactions
- Calculates and displays parking charges

### Manual Plate Capture
Click **"Manual Capture"** button in the GUI to trigger plate recognition without waiting for Arduino signal.

### Monitor Arduino Output (Optional)
```bash
# Use Arduino IDE Serial Monitor or:
python -m serial.tools.list_ports
```

## File Structure

```
CarParkingSystem/
├── main.py                          # Entry point - starts system & GUI
├── roi_selector.py                  # Interactive ROI configuration tool
├── roi_coordinates.json             # Saved ROI settings
├── parking_log.csv                  # Transaction history
├── arduino_code.ino                 # Arduino firmware (C++)
├── parking_system/
│   ├── core.py                      # Main system logic
│   ├── utils/
│   │   ├── camera_utils.py          # Camera initialization & frame capture
│   │   ├── serial_utils.py          # Arduino serial communication
│   │   ├── ocr_utils.py             # EasyOCR wrapper
│   │   ├── roi_utils.py             # ROI loading
│   │   └── log_utils.py             # CSV logging
│   └── __init__.py
├── gui/
│   ├── gui_main.py                  # Tkinter GUI interface
│   └── __init__.py
├── snapshots/                       # Captured vehicle images
├── LICENSE                          # MIT License
└── README.md                        # This file
```

## Usage Workflow

### 1. Vehicle Entry
- Car triggers IR entry sensor
- Gate opens (servo rotates)
- Camera captures license plate
- OCR recognizes and logs plate number with entry timestamp

### 2. Vehicle Parked
- Slot occupancy sensors update available spaces
- LCD displays parking status
- GUI shows real-time slot information

### 3. Vehicle Exit
- Car triggers IR exit sensor
- Gate opens
- Camera captures plate again
- System matches exit plate to entry log
- Calculates parking duration and charge
- Updates parking_log.csv
- Gate closes

### 4. GUI Dashboard
The Tkinter GUI displays:
- **Live Video Feed**: Real-time camera stream
- **Parking Status**: Available/occupied slots
- **Recent Logs**: Table of recent transactions with entry/exit times and charges
- **Manual Capture**: Button for manual plate recognition

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Camera not detected | Check camera index in code (default: 1), close other camera apps |
| Arduino connection fails | Verify COM port, check USB cable, install CH340 drivers |
| OCR not detecting plates | Run `roi_selector.py` to adjust ROI, improve lighting |
| GUI not responding | Check serial connection, restart Python script |
| Gate not opening | Verify servo motor connection, check Arduino power |

## Configuration

### Modify Pricing
Edit [parking_system/core.py](parking_system/core.py):
```python
system = ParkingSystem(..., price_per_min=2.0)  # ₹2 per minute
```

### Change Camera Index
```python
system = ParkingSystem(..., camera_index=0)  # Try 0, 1, 2, etc.
```

### Adjust Arduino COM Port
```python
system = ParkingSystem(serial_port="COM4", ...)
```

### Modify LCD Display Messages
Edit [arduino_code.ino](arduino_code.ino) and upload to Arduino

## License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

## Author

**Ramesh Kumar Singh** (2025)

## Support & Contribution

For issues, feature requests, or contributions, please open an issue or pull request on the repository.

---

**Last Updated**: November 2025