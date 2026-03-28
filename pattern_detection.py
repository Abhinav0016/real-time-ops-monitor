def create_issue(issue_type, severity, description, site=None, metrics=None):
    """Helper to create a structured issue dictionary."""
    issue = {
        "type": issue_type,
        "severity": severity,
        "description": description,
    }
    if site:
        issue["site"] = site
    if metrics:
        issue["metrics"] = metrics
    return issue

def detect_site_issues(device_metrics):
    """
    Detects site-level operational issues.
    - Site Outage: offline_devices >= 3 OR offline_percentage >= 80%
    - Degraded Site: offline_percentage between 40%-80%
    """
    issues = []
    for site, metrics in device_metrics.items():
        offline_count = metrics.get('offline_devices', 0)
        offline_pct = metrics.get('offline_percentage', 0)
        
        if offline_count >= 3 or offline_pct >= 80:
            issues.append(create_issue(
                "site_outage", "high",
                "Multiple devices offline or high failure rate indicating a site outage",
                site, metrics
            ))
        elif 40 <= offline_pct < 80:
            issues.append(create_issue(
                "site_degradation", "medium",
                "Significant number of devices offline, site performance degraded",
                site, metrics
            ))
    return issues

def detect_device_issues(device_metrics):
    """
    Detects device-level issues (simulated).
    - Unstable Device: IF any device is offline (simplified for this step)
    """
    issues = []
    for site, metrics in device_metrics.items():
        if metrics.get('offline_devices', 0) > 0:
            # Note: This is a simplification as per Step 4 requirements
            issues.append(create_issue(
                "unstable_device", "medium",
                "One or more devices at this site are currently offline or unstable",
                site
            ))
    return issues

def detect_alert_issues(alert_metrics):
    """
    Detects alert-based issues.
    - Critical Alert Presence: IF critical_alerts > 0
    """
    issues = []
    for site, metrics in alert_metrics.items():
        if metrics.get('critical_alerts', 0) > 0:
            issues.append(create_issue(
                "critical_alert", "high",
                "Critical system alerts detected at this site",
                site, metrics
            ))
    return issues

def detect_ticket_issues(ticket_metrics):
    """
    Detects ticket-related issues.
    - Ticket Backlog: IF open_tickets >= 3
    - Aging Ticket (SLA Risk): IF oldest_ticket_age > 3 days
    """
    issues = []
    for site, metrics in ticket_metrics.items():
        open_count = metrics.get('open_tickets', 0)
        oldest_age = metrics.get('oldest_ticket_age', 0)
        
        if open_count >= 3:
            issues.append(create_issue(
                "ticket_backlog", "medium",
                "High number of unresolved tickets at this site",
                site, metrics
            ))
        
        if oldest_age > 3:
            issues.append(create_issue(
                "sla_risk", "high",
                "Unresolved ticket exceeds 3-day SLA threshold",
                site, {"oldest_ticket_age": oldest_age}
            ))
    return issues

def detect_usage_issues(usage_metrics):
    """
    Detects global or regional usage issues.
    - High Usage (Usage Spike): IF trend == "increasing" AND percentage_change > 15
    """
    issues = []
    trend = usage_metrics.get('trend')
    pct_change = usage_metrics.get('percentage_change', 0)
    
    if trend == "increasing" and pct_change > 15:
        issues.append(create_issue(
            "usage_spike", "medium",
            f"Rapid usage increase detected ({pct_change}%)",
            metrics=usage_metrics
        ))
    return issues

def detect_all_issues(metrics):
    """
    Master pattern detection orchestrator.
    Combines all detection logic into a single list of issues.
    """
    all_detected = []
    
    all_detected.extend(detect_site_issues(metrics.get('device_metrics', {})))
    all_detected.extend(detect_device_issues(metrics.get('device_metrics', {})))
    all_detected.extend(detect_alert_issues(metrics.get('alert_metrics', {})))
    all_detected.extend(detect_ticket_issues(metrics.get('ticket_metrics', {})))
    all_detected.extend(detect_usage_issues(metrics.get('usage_metrics', {})))
    
    return all_detected
