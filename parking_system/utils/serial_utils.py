# parking_system/utils/serial_utils.py
import serial

def init_serial(port="COM3", baud=9600):
    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"[SERIAL] Connected to {port} at {baud} baud.")
        return ser
    except Exception as e:
        print(f"[ERROR] Serial connection failed: {e}")
        return None

def read_serial_line(ser):
    if ser and ser.in_waiting > 0:
        try:
            return ser.readline().decode().strip()
        except Exception as e:
            print(f"[ERROR] Serial read failed: {e}")
    return None
