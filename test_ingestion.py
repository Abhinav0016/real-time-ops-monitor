from ingestion_prometheus import get_live_dashboard_data
import json

def test_ingestion():
    print("Testing API-First Data Ingestion...")
    data = get_live_dashboard_data(use_mock=True)
    
    # Check if all keys exist
    expected_keys = ["devices", "alerts", "usage", "tickets", "maintenance"]
    for key in expected_keys:
        if key in data:
            print(f"[PASS] Key '{key}' found with {len(data[key])} records.")
        else:
            print(f"[FAIL] Key '{key}' missing from structured data.")
            
    # Check Site Density
    sites = set(d.get('site_name') for d in data.get('devices', []))
    print(f"Detected {len(sites)} unique sites: {sites}")
    
    # Check Alert Site Association
    unknown_alerts = [a for a in data.get('alerts', []) if a.get('site_name') == "Unknown Site"]
    if unknown_alerts:
        print(f"[FAIL] Found {len(unknown_alerts)} alerts with 'Unknown Site'.")
    else:
        print("[PASS] All alerts correctly attributed to sites.")

    print("\nSample Alert Record:")
    if data["alerts"]:
        print(json.dumps(data["alerts"][0], indent=2))
        
    print(f"\nTotal Tickets: {len(data['tickets'])}")

if __name__ == "__main__":
    test_ingestion()
