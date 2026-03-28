import json
from ingestion import load_all_data
from preprocessing import preprocess_data
from feature_extraction import extract_features
from pattern_detection import detect_all_issues
from intelligence_layer import process_intelligence_layer
from decision_layer import process_decision_layer
from ai_briefing import generate_briefing

def test_ai_briefing():
    print("Testing AI Briefing Layer...")
    
    # 1. Full Pipeline
    raw_data = load_all_data()
    preprocessed = preprocess_data(raw_data)
    features = extract_features(preprocessed)
    detected_issues = detect_all_issues(features)
    intelligence_output = process_intelligence_layer(detected_issues, features, preprocessed)
    decision_output = process_decision_layer(intelligence_output, features)
    
    # Combine outputs for AI input
    final_data = {
        "top_priorities": intelligence_output["top_priorities"],
        "all_issues": intelligence_output["all_issues"],
        "predictions": decision_output["predictions"],
        "recommendations": decision_output["recommendations"]
    }
    
    # 2. Generate Briefing (Fleet Manager)
    print("\n[TEST] Generating Briefing for Fleet Manager...")
    briefing_fleet = generate_briefing(final_data, features, role="Fleet Manager")
    
    if "briefing_text" in briefing_fleet:
        print("[PASS] Briefing text generated successfully.")
        print("-" * 30)
        print(briefing_fleet["briefing_text"])
        print("-" * 30)
    else:
        print("[FAIL] Briefing text NOT generated.")

    # 3. Generate Briefing (NOC Analyst)
    print("\n[TEST] Generating Briefing for NOC Analyst...")
    briefing_noc = generate_briefing(final_data, features, role="NOC Analyst")
    
    if "briefing_text" in briefing_noc:
        print("[PASS] Briefing text generated successfully.")
    else:
        print("[FAIL] Briefing text NOT generated.")

if __name__ == "__main__":
    test_ai_briefing()
