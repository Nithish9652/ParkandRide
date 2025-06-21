# utils/occupancy_report.py
import os, json
from datetime import datetime

LOG_FILE = os.getenv("BOOKING_LOG_FILE", "realtime.log")
TOTAL_SLOTS = 20 * 20

def current_occupancy(at: datetime = None) -> int:
    at = at or datetime.utcnow()
    reservations = {}

    if not os.path.exists(LOG_FILE):
        return 0

    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                action = entry["action"].upper()
                key = (entry["row"], entry["col"])
                start = datetime.fromisoformat(entry["start"])
                end   = datetime.fromisoformat(entry["end"])
            except (ValueError, KeyError):
                continue  # skip malformed

            if action == "BOOKING":
                reservations[key] = (start, end)
            elif action == "CANCEL":
                reservations.pop(key, None)

    return sum(1 for s, e in reservations.values() if s <= at < e)

def report_availability():
    now = datetime.utcnow()
    occupied = current_occupancy(now)
    free = TOTAL_SLOTS - occupied
    print(f"[{now.isoformat()} UTC]    Occupied: {occupied}/{TOTAL_SLOTS}    Free: {free}")

if __name__ == "__main__":
    report_availability()