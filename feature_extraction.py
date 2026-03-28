def extract_device_metrics(devices_by_site):
    """
    Extracts device health metrics per site.
    - total_devices
    - offline_devices
    - online_devices
    - offline_percentage
    """
    metrics = {}
    for site, devices in devices_by_site.items():
        total = len(devices)
        offline = sum(1 for d in devices if d.get('status') == 'offline')
        online = total - offline
        offline_pct = (offline / total * 100) if total > 0 else 0
        
        metrics[site] = {
            "total_devices": total,
            "offline_devices": offline,
            "online_devices": online,
            "offline_percentage": round(offline_pct, 2)
        }
    return metrics

def extract_alert_metrics(alerts_by_site):
    """
    Extracts alert metrics per site.
    - total_alerts
    - critical_alerts
    - warning_alerts
    """
    metrics = {}
    for site, alerts in alerts_by_site.items():
        total = len(alerts)
        critical = sum(1 for a in alerts if a.get('severity') == 'critical')
        warning = sum(1 for a in alerts if a.get('severity') == 'warning')
        
        metrics[site] = {
            "total_alerts": total,
            "critical_alerts": critical,
            "warning_alerts": warning
        }
    return metrics

def extract_ticket_metrics(tickets_by_site):
    """
    Extracts ticket metrics per site.
    - total_tickets
    - open_tickets
    - high_priority_tickets
    - oldest_ticket (age_days)
    """
    metrics = {}
    for site, tickets in tickets_by_site.items():
        total = len(tickets)
        open_tickets = sum(1 for t in tickets if t.get('status') == 'open')
        high_priority = sum(1 for t in tickets if t.get('priority', '').lower() == 'high')
        
        # Identify oldest ticket
        oldest = 0
        if tickets:
            oldest = max((t.get('age_days', 0) for t in tickets), default=0)
            
        metrics[site] = {
            "total_tickets": total,
            "open_tickets": open_tickets,
            "high_priority_tickets": high_priority,
            "oldest_ticket_age": oldest
        }
    return metrics

def extract_usage_metrics(usage_records, usage_by_site=None):
    """
    Calculates global usage metrics and site-specific snapshots.
    - site_usage: Dict of latest GB per site
    - trend: 'increasing', 'decreasing', 'stable'
    """
    site_usage = {}
    if usage_by_site:
        for site, records in usage_by_site.items():
            if records:
                # Latest record for this site
                site_usage[site] = records[-1].get('data_usage_gb', 0)

    if not usage_records or len(usage_records) < 2:
        return {
            "trend": "unknown",
            "percentage_change": 0,
            "total_usage_gb": sum(u.get('data_usage_gb', 0) for u in usage_records),
            "site_usage": site_usage
        }
    
    last = usage_records[-1].get('data_usage_gb', 0)
    prev = usage_records[-2].get('data_usage_gb', 0)
    
    diff = last - prev
    pct_change = (diff / prev * 100) if prev > 0 else 0
    
    trend = "stable"
    if diff > 0.01:
        trend = "increasing"
    elif diff < -0.01:
        trend = "decreasing"
        
    return {
        "trend": trend,
        "percentage_change": round(pct_change, 2),
        "last_usage_gb": last,
        "previous_usage_gb": prev,
        "site_usage": site_usage
    }

def extract_global_metrics(data, preprocessed):
    """
    Calculates global system-wide KPIs.
    - total_sites
    - total_devices
    - total_offline_devices
    - total_critical_alerts
    - total_open_tickets
    """
    site_summary = preprocessed.get('site_summary', {})
    total_sites = len(site_summary)
    
    total_devices = sum(s.get('total_devices', 0) for s in site_summary.values())
    total_offline = sum(s.get('offline_devices', 0) for s in site_summary.values())
    
    total_critical_alerts = 0
    for site_alerts in preprocessed.get('alerts_by_site', {}).values():
        total_critical_alerts += sum(1 for a in site_alerts if a.get('severity') == 'critical')
        
    total_open_tickets = 0
    for site_tickets in preprocessed.get('tickets_by_site', {}).values():
        total_open_tickets += sum(1 for t in site_tickets if t.get('status') == 'open')
        
    return {
        "total_sites": total_sites,
        "total_devices": total_devices,
        "total_offline_devices": total_offline,
        "total_critical_alerts": total_critical_alerts,
        "total_open_tickets": total_open_tickets
    }

def extract_features(preprocessed_data):
    """
    Master feature extraction orchestrator.
    """
    device_metrics = extract_device_metrics(preprocessed_data.get('devices_by_site', {}))
    alert_metrics = extract_alert_metrics(preprocessed_data.get('alerts_by_site', {}))
    ticket_metrics = extract_ticket_metrics(preprocessed_data.get('tickets_by_site', {}))
    usage_metrics = extract_usage_metrics(preprocessed_data.get('usage', []), preprocessed_data.get('usage_by_site', {}))
    global_metrics = extract_global_metrics({}, preprocessed_data)
    
    return {
        "device_metrics": device_metrics,
        "alert_metrics": alert_metrics,
        "ticket_metrics": ticket_metrics,
        "usage_metrics": usage_metrics,
        "global_metrics": global_metrics
    }
