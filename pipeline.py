import logging
from ingestion import load_all_data
from preprocessing import preprocess_data
from feature_extraction import extract_features
from pattern_detection import detect_all_issues
from intelligence_layer import process_intelligence_layer
from decision_layer import process_decision_layer
from ai_briefing import generate_briefing

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_daily_briefing(role="Fleet Manager", api_key=None):
    """
    Unified integration pipeline for telecom operations briefing.
    Calls all 7 functional layers sequentially and returns a structured response.
    """
    try:
        # 1. Load Data
        logger.info("Step 1: Ingesting raw data...")
        raw_data = load_all_data()
        
        # 2. Preprocess Data
        logger.info("Step 2: Preprocessing...")
        preprocessed = preprocess_data(raw_data)
        
        # 3. Extract Features
        logger.info("Step 3: Calculating metrics and trends...")
        features = extract_features(preprocessed)
        
        # 4. Detect Issues
        logger.info("Step 4: Detecting patterns/issues...")
        detected_issues = detect_all_issues(features)
        
        # 5. Intelligence Layer (Enrich + Rank)
        logger.info("Step 5: Prioritizing and enriching issues...")
        intelligence_output = process_intelligence_layer(detected_issues, features, preprocessed)
        
        # 6. Predictions and Recommendations
        logger.info("Step 6: Generating predictions and recommendations...")
        decision_output = process_decision_layer(intelligence_output, features)
        
        # 7. AI Briefing
        logger.info("Step 7: Generating AI report...")
        final_data_for_ai = {
            "top_priorities": intelligence_output["top_priorities"],
            "all_issues": intelligence_output["all_issues"],
            "predictions": decision_output["predictions"],
            "recommendations": decision_output["recommendations"]
        }
        briefing_output = generate_briefing(final_data_for_ai, features, role=role, api_key=api_key)
        
        # Construct Final Response
        result = {
            "status": "success",
            "role": role,
            "top_priorities": intelligence_output["top_priorities"],
            "issues": intelligence_output["all_issues"],
            "predictions": decision_output["predictions"],
            "recommendations": decision_output["recommendations"],
            "briefing": briefing_output["briefing_text"]
        }
        
        logger.info("Pipeline executed successfully.")
        return result

    except Exception as e:
        logger.error(f"Pipeline failed at some step: {e}")
        return {
            "status": "error",
            "message": str(e),
            "role": role
        }
