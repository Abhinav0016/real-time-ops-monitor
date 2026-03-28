def enrich_issues(detected_issues, metrics):
    """
    Adds contextual metrics to each detected issue.
    - affected_devices
    - related_tickets
    - critical_alerts
    """
    for issue in detected_issues:
        site = issue.get('site')
        if not site:
            # Global issues or issues without a site
            issue['affected_devices'] = metrics.get('global_metrics', {}).get('total_devices', 0)
            issue['related_tickets'] = metrics.get('global_metrics', {}).get('total_open_tickets', 0)
            issue['critical_alerts'] = metrics.get('global_metrics', {}).get('total_critical_alerts', 0)
            continue
            
        # Site-specific metrics
        device_m = metrics.get('device_metrics', {}).get(site, {})
        ticket_m = metrics.get('ticket_metrics', {}).get(site, {})
        alert_m = metrics.get('alert_metrics', {}).get(site, {})
        
        issue['affected_devices'] = device_m.get('offline_devices', 0)
        issue['related_tickets'] = ticket_m.get('open_tickets', 0)
        issue['critical_alerts'] = alert_m.get('critical_alerts', 0)
        
    return detected_issues

def calculate_priority(enriched_issues):
    """
    Assigns a priority_score based on issue type and impact.
    """
    base_scores = {
        "site_outage": 5,
        "critical_alert": 4,
        "ticket_backlog": 3,
        "unstable_device": 3,
        "sla_risk": 3,
        "usage_spike": 2,
        "site_degradation": 3
    }
    
    for issue in enriched_issues:
        score = base_scores.get(issue.get('type'), 1)
        
        # Impact multipliers
        if issue.get('affected_devices', 0) > 3:
            score += 2
        
        if issue.get('related_tickets', 0) > 2:
            score += 2
            
        issue['priority_score'] = score
        
    return enriched_issues

def correlate_issues(enriched_issues, preprocessed_data):
    """
    Links specific tickets and alerts from the preprocessed data to site-related issues.
    """
    for issue in enriched_issues:
        site = issue.get('site')
        if not site:
            continue
            
        # Link related data
        linked_tickets = preprocessed_data.get('tickets_by_site', {}).get(site, [])
        linked_alerts = preprocessed_data.get('alerts_by_site', {}).get(site, [])
        
        issue['linked_data'] = {
            "tickets": linked_tickets,
            "alerts": linked_alerts
        }
        
    return enriched_issues

def rank_issues(scored_issues):
    """
    Sorts issues by priority_score and selects top 3.
    """
    sorted_issues = sorted(scored_issues, key=lambda x: x.get('priority_score', 0), reverse=True)
    top_priorities = sorted_issues[:3]
    return sorted_issues, top_priorities

def process_intelligence_layer(detected_issues, metrics, preprocessed):
    """
    Master intelligence layer orchestrator.
    """
    # 1. Enrich
    enriched = enrich_issues(detected_issues, metrics)
    
    # 2. Score
    scored = calculate_priority(enriched)
    
    # 3. Correlate
    correlated = correlate_issues(scored, preprocessed)
    
    # 4. Rank
    all_ranked, top_3 = rank_issues(correlated)
    
    return {
        "all_issues": all_ranked,
        "top_priorities": top_3
    }
