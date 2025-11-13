# main.py
from parking_system import ParkingSystem
from gui import ParkingGUI

def main():
    system = ParkingSystem()   # create the backend system (camera, serial, OCR, logs)
    gui = ParkingGUI(system)   # create GUI that interacts with it
    gui.run()                  # start GUI (blocking)
    system.cleanup()           # cleanup resources when GUI is closed

if __name__ == "__main__":
    main()
