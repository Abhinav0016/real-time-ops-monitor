import json
from ingestion import load_all_data
from preprocessing import preprocess_data
from feature_extraction import extract_features
from pattern_detection import detect_all_issues

def test_pattern_detection():
    print("Testing Pattern Detection Layer...")
    
    # 1. Full Pipeline
    raw_data = load_all_data()
    preprocessed = preprocess_data(raw_data)
    features = extract_features(preprocessed)
    
    # 2. Detect Issues
    issues = detect_all_issues(features)
    
    # 3. Verification
    
    # Check for expected issues
    issue_types = [i["type"] for i in issues]
    print(f"Detected Issues: {issue_types}")
    
    # Expected: site_outage (Site B), ticket_backlog (Site A), sla_risk (Site A), usage_spike (Global), critical_alert (Site B)
    expected = ["site_outage", "ticket_backlog", "sla_risk", "usage_spike", "critical_alert"]
    
    for exp_type in expected:
        if exp_type in issue_types:
            print(f"[PASS] Issue type '{exp_type}' correctly detected.")
        else:
            print(f"[FAIL] Issue type '{exp_type}' NOT detected.")
            
    # Check details for Site B outage
    b_outage = next((i for i in issues if i["type"] == "site_outage" and i.get("site") == "Site B"), None)
    if b_outage:
        print(f"[PASS] Site B Outage found: {b_outage['description']}")
    else:
        print("[FAIL] Site B Outage NOT found.")

    # Check details for Site A backlog
    a_backlog = next((i for i in issues if i["type"] == "ticket_backlog" and i.get("site") == "Site A"), None)
    if a_backlog:
        print(f"[PASS] Site A Backlog found: {a_backlog['description']} ({a_backlog['metrics']['open_tickets']} open)")
    else:
        print("[FAIL] Site A Backlog NOT found.")

    print("\nPattern Detection Output (Sample):")
    print(json.dumps(issues, indent=2))

if __name__ == "__main__":
    test_pattern_detection()
