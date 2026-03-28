def generate_predictions(intelligence_output, metrics):
    """
    Generates simple, rule-based predictions for the system.
    """
    predictions = []
    usage_m = metrics.get('usage_metrics', {})
    all_issues = intelligence_output.get('all_issues', [])
    
    # A. Usage Prediction
    if usage_m.get('trend') == "increasing" and usage_m.get('percentage_change', 0) > 15:
        predictions.append({
            "type": "usage_overflow",
            "message": "Data usage is increasing rapidly and may exceed limit soon",
            "confidence": "high"
        })
        
    # B. Site Risk Prediction
    # Check if site_outage exists and related_tickets > 2
    for issue in all_issues:
        if issue.get('type') == 'site_outage' and issue.get('related_tickets', 0) > 2:
            predictions.append({
                "type": "site_failure_risk",
                "site": issue.get('site'),
                "message": "Site may experience prolonged outage if not resolved",
                "confidence": "medium"
            })
            
    # C. SLA Risk
    # Check if any sla_risk issue exists
    if any(i.get('type') == 'sla_risk' for i in all_issues):
        predictions.append({
            "type": "sla_breach",
            "message": "Some tickets may breach SLA if not addressed soon",
            "confidence": "high"
        })
        
    return predictions

def generate_recommendations(intelligence_output):
    """
    Generates actionable suggestions based on identified issue types.
    """
    recommendations = []
    seen_types = set()
    
    # We map recommendations by issue type
    rules = {
        "site_outage": "Restart affected terminals or dispatch field technician",
        "critical_alert": "Investigate connectivity issues immediately",
        "ticket_backlog": "Escalate pending tickets and assign resources",
        "unstable_device": "Monitor device and consider replacement",
        "usage_spike": "Optimize bandwidth usage or upgrade data plan",
        "sla_risk": "Prioritize aging tickets to avoid SLA breach"
    }
    
    all_issues = intelligence_output.get('all_issues', [])
    for issue in all_issues:
        issue_type = issue.get('type')
        if issue_type in rules and issue_type not in seen_types:
            recommendations.append({
                "issue_type": issue_type,
                "action": rules[issue_type]
            })
            seen_types.add(issue_type)
            
    return recommendations

def process_decision_layer(intelligence_output, metrics):
    """
    Master decision layer orchestrator.
    """
    predictions = generate_predictions(intelligence_output, metrics)
    recommendations = generate_recommendations(intelligence_output)
    
    return {
        "predictions": predictions,
        "recommendations": recommendations
    }
