from ingestion import load_all_data
import json

def test_ingestion():
    print("Testing Data Ingestion Layer...")
    data = load_all_data()
    
    # Check if all keys exist
    expected_keys = ["devices", "alerts", "usage", "tickets", "maintenance"]
    for key in expected_keys:
        if key in data:
            print(f"[PASS] Key '{key}' found with {len(data[key])} records.")
        else:
            print(f"[FAIL] Key '{key}' missing from structured data.")
            
    # Check normalization
    if data["devices"]:
        device = data["devices"][0]
        site_name_normalized = device.get("site_name") == "Site A"
        status_normalized = (device.get("status") == "online")
        
        if site_name_normalized:
            print("[PASS] Site name normalization works ('site a' -> 'Site A').")
        else:
            print(f"[FAIL] Site name normalization failed: {device.get('site_name')}")
            
        if status_normalized:
            print("[PASS] Status normalization works ('Online' -> 'online').")
        else:
            print(f"[FAIL] Status normalization failed: {device.get('status')}")

if __name__ == "__main__":
    test_ingestion()
