import json
from ingestion import load_all_data
from preprocessing import preprocess_data

def test_preprocessing():
    print("Testing Preprocessing Layer...")
    
    # 1. Load raw data
    raw_data = load_all_data()
    
    # 2. Preprocess
    preprocessed = preprocess_data(raw_data)
    
    # 3. Verification
    
    # Check output keys
    expected_keys = [
        "devices_by_site", 
        "alerts_by_site", 
        "tickets_by_site", 
        "usage", 
        "maintenance", 
        "site_summary"
    ]
    for key in expected_keys:
        if key in preprocessed:
            print(f"[PASS] Key '{key}' found.")
        else:
            print(f"[FAIL] Key '{key}' missing.")
            
    # Check grouping
    if "Site A" in preprocessed["devices_by_site"]:
        print("[PASS] Devices grouped by site correctly ('Site A' found).")
    else:
        print("[FAIL] Site A missing from devices_by_site.")
        
    # Check site summary
    if "Site A" in preprocessed["site_summary"]:
        summary = preprocessed["site_summary"]["Site A"]
        print(f"[PASS] Site A Summary: {summary}")
        if summary["total_devices"] > 0:
            print(f"[PASS] Site A has {summary['total_devices']} total devices.")
        else:
            print("[FAIL] Site A should have devices.")
    else:
        print("[FAIL] Site A missing from site_summary.")

    # Check alert grouping by site (device location)
    if "Site B" in preprocessed["alerts_by_site"]:
         print("[PASS] Alerts grouped by site (via device location) correctly.")
    else:
         print("[FAIL] Alerts missing for Site B (where TWR-002 is located).")

    # Check normalization within preprocessed data
    if "usage" in preprocessed and len(preprocessed["usage"]) > 0:
        region = preprocessed["usage"][0].get('region')
        if region == "North": # "north" was normalized in step 1 too, but let's confirm
            print(f"[PASS] Usage region normalization: {region}")

    # Print a sample of preprocessed data
    print("\nPreprocessed Site Summary:")
    print(json.dumps(preprocessed["site_summary"], indent=2))
    
    print("\nFull Preprocessed Data (Sample):")
    # Just show keys and counts to keep it clean
    for key, value in preprocessed.items():
        if isinstance(value, dict):
            print(f"{key}: {list(value.keys())}")
        elif isinstance(value, list):
            print(f"{key}: {len(value)} records")

if __name__ == "__main__":
    test_preprocessing()
