import json
from ingestion import load_all_data
from preprocessing import preprocess_data
from feature_extraction import extract_features
from pattern_detection import detect_all_issues
from intelligence_layer import process_intelligence_layer

def test_intelligence():
    print("Testing Intelligence Layer...")
    
    # 1. Full Pipeline
    raw_data = load_all_data()
    preprocessed = preprocess_data(raw_data)
    features = extract_features(preprocessed)
    detected_issues = detect_all_issues(features)
    
    # 2. Intelligence Layer
    intelligence_output = process_intelligence_layer(detected_issues, features, preprocessed)
    
    # 3. Verification
    
    # Check output keys
    expected_keys = ["all_issues", "top_priorities"]
    for key in expected_keys:
        if key in intelligence_output:
            print(f"[PASS] Key '{key}' found.")
        else:
            print(f"[FAIL] Key '{key}' missing.")
            
    all_issues = intelligence_output["all_issues"]
    top_3 = intelligence_output["top_priorities"]
    
    # Check Enrichment and Scoring for Site B Output
    site_b_outage = next((i for i in all_issues if i["type"] == "site_outage" and i.get("site") == "Site B"), None)
    if site_b_outage:
        print(f"[PASS] Site B Outage found.")
        if "affected_devices" in site_b_outage and "priority_score" in site_b_outage:
             print(f"[PASS] Site B Outage enriched and scored: Score={site_b_outage['priority_score']}, Affected Devices={site_b_outage['affected_devices']}")
             # Site B Outage score should be Base 5.
             # Site B has 3 devices, all offline. So 100%. affected_devices = 3. 
             # Multipliers: affected_devices > 3 (no), related_tickets > 2 (no).
             # Wait, Site B has 3 devices (TWR-002, TWR-004, TWR-005). 
             # So affected_devices = 3. No +2 boost.
             if site_b_outage['priority_score'] == 5:
                 print(f"[PASS] Priority score correctly calculated (5).")
        else:
             print(f"[FAIL] Enrichment or scoring missing for Site B.")
             
        if "linked_data" in site_b_outage:
             print(f"[PASS] Linked data found for Site B. Alerts: {len(site_b_outage['linked_data']['alerts'])}")
    else:
        print("[FAIL] Site B Outage NOT found in enriched issues.")

    # Check Top Priorities (should be sorted)
    if len(top_3) > 0:
        print(f"[PASS] Top priorities found: {len(top_3)}")
        scores = [i["priority_score"] for i in top_3]
        if scores == sorted(scores, reverse=True):
            print(f"[PASS] Top priorities are correctly ranked by score: {scores}")
        else:
            print(f"[FAIL] Top priorities not ranked correctly: {scores}")

    print("\nIntelligence Layer Output (Sample):")
    # Show top priorities
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)

    from datetime import datetime
    print(json.dumps(intelligence_output["top_priorities"], indent=2, cls=DateTimeEncoder))

if __name__ == "__main__":
    test_intelligence()
