import sys
import os
from datetime import datetime
import pandas as pd

# Add backend to path to import detection
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from detection import get_all_data

def debug_alerts():
    print(f"Current System Time: {datetime.now()}")
    print("Fetching data and briefing...")
    data = get_all_data(role="Fleet Operations Manager")
    
    critical = data.get('results', {}).get('critical', [])
    print(f"\nCritical Alerts ({len(critical)} found):")
    for alert in critical:
        print(f"  - {alert}")
    
    if not critical:
        print("  NO CRITICAL ALERTS DETECTED.")
        # Check why
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATA_DIR = os.path.join(BASE_DIR, "datasetss")
        devices = pd.read_csv(os.path.join(DATA_DIR, "devices_v2.csv"))
        print("\nOffline devices in CSV:")
        off = devices[devices['status'] == 'offline']
        print(off[['device_id', 'status', 'last_seen']])

if __name__ == "__main__":
    debug_alerts()
