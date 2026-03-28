import json
from ingestion import load_all_data
from preprocessing import preprocess_data
from feature_extraction import extract_features

def test_feature_extraction():
    print("Testing Feature Extraction Layer...")
    
    # 1. Load and Preprocess
    raw_data = load_all_data()
    preprocessed = preprocess_data(raw_data)
    
    # 2. Extract Features
    features = extract_features(preprocessed)
    
    # 3. Verification
    
    # Check output keys
    expected_keys = [
        "device_metrics", 
        "alert_metrics", 
        "ticket_metrics", 
        "usage_metrics", 
        "global_metrics"
    ]
    for key in expected_keys:
        if key in features:
            print(f"[PASS] Key '{key}' found.")
        else:
            print(f"[FAIL] Key '{key}' missing.")
            
    # Check Device Metrics for Site B (should be 1 device, 1 offline)
    if "Site B" in features["device_metrics"]:
        m = features["device_metrics"]["Site B"]
        if m["offline_devices"] == 1 and m["offline_percentage"] == 100.0:
            print("[PASS] Device metrics for Site B are correct (100% offline).")
        else:
            print(f"[FAIL] Device metrics for Site B incorrect: {m}")
            
    # Check Alert Metrics for Site B (should have 1 critical alert)
    if "Site B" in features["alert_metrics"]:
        m = features["alert_metrics"]["Site B"]
        if m["critical_alerts"] == 1:
            print("[PASS] Alert metrics for Site B are correct (1 critical).")
        else:
            print(f"[FAIL] Alert metrics for Site B incorrect: {m}")

    # Check Ticket Metrics for Site A (should have 2 tickets, 1 high priority, oldest 5 days)
    if "Site A" in features["ticket_metrics"]:
        m = features["ticket_metrics"]["Site A"]
        if m["total_tickets"] == 2 and m["high_priority_tickets"] == 1 and m["oldest_ticket_age"] == 5:
            print("[PASS] Ticket metrics for Site A are correct (2 total, 1 high-pri, oldest 5d).")
        else:
            print(f"[FAIL] Ticket metrics for Site A incorrect: {m}")

    # Check Usage Trends (North region usage went 1000 -> 1100 -> 1342)
    m = features["usage_metrics"]
    if m["trend"] == "increasing":
        print(f"[PASS] Usage trend correctly identified: {m['trend']} ({m['percentage_change']}% change)")
    else:
        print(f"[FAIL] Usage trend incorrect: {m}")

    # Check Global Metrics
    g = features["global_metrics"]
    if g["total_sites"] >= 2 and g["total_devices"] == 3 and g["total_offline_devices"] == 1:
        print(f"[PASS] Global metrics correct: {g}")
    else:
        print(f"[FAIL] Global metrics incorrect: {g}")

    print("\nFeature Extraction Output (Sample):")
    print(json.dumps(features, indent=2))

if __name__ == "__main__":
    test_feature_extraction()
