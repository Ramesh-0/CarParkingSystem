# parking_system/utils/log_utils.py
import pandas as pd

def save_parking_log(plate, entry, exit, duration, cost, filename="parking_log.csv"):
    df = pd.DataFrame([[plate, entry, exit, duration, cost]],
                      columns=["Plate", "Entry Time", "Exit Time", "Minutes", "Cost"])
    df.to_csv(filename, mode='a', index=False, header=not pd.io.common.file_exists(filename))
    print(f"[LOG] Saved entry for {plate}")
