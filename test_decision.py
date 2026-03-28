import json
from ingestion import load_all_data
from preprocessing import preprocess_data
from feature_extraction import extract_features
from pattern_detection import detect_all_issues
from intelligence_layer import process_intelligence_layer
from decision_layer import process_decision_layer

def test_decision_layer():
    print("Testing Prediction and Recommendation Layer...")
    
    # 1. Full Pipeline
    raw_data = load_all_data()
    preprocessed = preprocess_data(raw_data)
    features = extract_features(preprocessed)
    detected_issues = detect_all_issues(features)
    intelligence_output = process_intelligence_layer(detected_issues, features, preprocessed)
    
    # 2. Decision Layer
    decision_output = process_decision_layer(intelligence_output, features)
    
    # 3. Verification
    
    # Check output keys
    expected_keys = ["predictions", "recommendations"]
    for key in expected_keys:
        if key in decision_output:
            print(f"[PASS] Key '{key}' found.")
        else:
            print(f"[FAIL] Key '{key}' missing.")
            
    # Check for Usage Prediction (should be usage_overflow due to 22% increase)
    predictions = decision_output["predictions"]
    overflow_pred = next((p for p in predictions if p["type"] == "usage_overflow"), None)
    if overflow_pred:
        print(f"[PASS] Usage overflow prediction found: {overflow_pred['message']}")
    else:
        print("[FAIL] Usage overflow prediction NOT found.")

    # Check for SLA Risk Prediction (should be sla_breach since Site A has old tickets)
    sla_pred = next((p for p in predictions if p["type"] == "sla_breach"), None)
    if sla_pred:
        print(f"[PASS] SLA breach prediction found: {sla_pred['message']}")
    else:
        print("[FAIL] SLA breach prediction NOT found.")

    # Check for Recommendations (should have site_outage, usage_spike, etc.)
    recommendations = decision_output["recommendations"]
    rec_types = [r["issue_type"] for r in recommendations]
    print(f"Generated Recommendations for: {rec_types}")
    
    expected_rec_types = ["site_outage", "usage_spike", "sla_risk"]
    for ext in expected_rec_types:
        if ext in rec_types:
            print(f"[PASS] Recommendation for '{ext}' generated.")
        else:
            print(f"[FAIL] Recommendation for '{ext}' NOT generated.")

    print("\nDecision Layer Output (Full):")
    print(json.dumps(decision_output, indent=2))

if __name__ == "__main__":
    test_decision_layer()
