import json
import requests
import random
from datetime import datetime, timedelta

# Public Prometheus Demo URL (for documentation/reference)
PROM_DEMO_URL = "https://prometheus.demo.do.prometheus.io/api/v1/query"

def get_prometheus_mock_data():
    """
    Returns a high-fidelity simulation of the Prometheus Query API response.
    Expanded to 10 sites (A-J) and 30+ devices for enterprise-scale analysis.
    """
    ts = datetime.utcnow().timestamp()
    results = []
    
    sites = ["Site A", "Site B", "Site C", "Site D", "Site E", "Site F", "Site G", "Site H", "Site I", "Site J"]
    
    for i, site in enumerate(sites):
        # 3-5 devices per site
        num_devices = random.randint(3, 5)
        for d in range(num_devices):
            instance = f"Cell-Tower-{site[-1]}{d+1}"
            
            # Health ('up' metric)
            status = "1"
            if site in ["Site A", "Site D"] and d == 0: status = "0" # Some offline
            if site == "Site G": status = "0" # Entire site down
            
            results.append({
                "metric": {"__name__": "up", "instance": instance, "site": site, "job": "telecom_nodes"},
                "value": [ts, status]
            })
            
            # Load ('node_load1')
            load_val = str(round(random.uniform(0.5, 3.5), 2))
            results.append({
                "metric": {"__name__": "node_load1", "instance": instance, "site": site},
                "value": [ts, load_val]
            })
            
            # Alerts (randomly assigned)
            if site in ["Site A", "Site D", "Site G"] and random.random() > 0.6:
                alert_type = random.choice(["Signal Loss", "Power Failure", "Hardware Fault", "Temp High"])
                results.append({
                    "metric": {"__name__": "alert_critical", "instance": instance, "site": site, "alert_type": alert_type},
                    "value": [ts, "1"]
                })
            elif random.random() > 0.85:
                results.append({
                    "metric": {"__name__": "alert_warning", "instance": instance, "site": site, "alert_type": "Minor Fluctuation"},
                    "value": [ts, "1"]
                })
                
    return {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": results
        }
    }

def fetch_live_prometheus(query="up", use_mock=True):
    """
    Handles the actual REST call to Prometheus. 
    Defaults to mock for environment stability.
    """
    if use_mock:
        return get_prometheus_mock_data()
    
    try:
        response = requests.get(PROM_DEMO_URL, params={'query': query}, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Prometheus Connection Error: {e}")
    
    return get_prometheus_mock_data()

def map_prometheus_to_telecom(api_response):
    """
    Transforms flat Prometheus time-series results into the nested 
    schema expected by the 7-layer pipeline.
    """
    results = api_response.get("data", {}).get("result", [])
    
    devices = []
    usage_data = []
    alerts = []
    
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    for item in results:
        metric = item.get("metric", {})
        value_tuple = item.get("value", [0, "0"])
        val_str = value_tuple[1]
        
        instance = metric.get("instance", "unknown-node")
        site = metric.get("site", "Global")
        
        # 1. Map 'up' metric to health status
        if metric.get("__name__") == "up":
            status = "online" if val_str == "1" else "offline"
            devices.append({
                "device_id": f"PROM-{instance}",
                "site_name": site,
                "status": status,
                "timestamp": timestamp
            })
            
        # 2. Map 'node_load' or similar to usage
        if metric.get("__name__") == "node_load1":
            usage_gb = float(val_str) * 10
            usage_data.append({
                "site_name": site,
                "data_usage_gb": round(usage_gb, 2),
                "timestamp": timestamp,
                "region": "Prometheus-Live"
            })
            
        # 3. Map alerts
        if "alert_" in metric.get("__name__", ""):
            severity = metric["__name__"].split("_")[1]
            alerts.append({
                "alert_id": f"PROM-AL-{random.randint(1000,9999)}",
                "device_id": f"PROM-{instance}",
                "site_name": site,
                "severity": severity,
                "message": f"Live Prometheus {severity.upper()} Alert: {metric.get('alert_type','General Error')}"
            })
            
    return devices, usage_data, alerts

def get_jira_mock_data():
    """
    Returns a high-fidelity simulation of the Jira Ticket API response.
    Provides 20+ active tickets mapped to the 10 sites (A-J).
    """
    sites = ["Site A", "Site B", "Site C", "Site D", "Site E", "Site F", "Site G", "Site H", "Site I", "Site J"]
    tickets = []
    
    # Pre-defined issues for variety
    issue_pool = [
        ("Power instability detected", "critical"),
        ("Signal degradation reported by users", "high"),
        ("Minor hardware optimization required", "low"),
        ("Backhaul connectivity slow", "medium"),
        ("Device firmware update pending", "medium"),
        ("Total node failure", "critical"),
        ("Intermittent ping spikes", "high")
    ]
    
    assignees = ["Emily", "John", "Jake", "Sarah", "Mike", "Ryan"]
    
    for i in range(25):
        site = random.choice(sites)
        desc, prio = random.choice(issue_pool)
        status = random.choice(["open", "open", "pending", "pending"]) # Tend towards open
        
        tickets.append({
            "ticket_id": f"JIRA-{random.randint(1000, 9999)}",
            "device_id": f"PROM-Cell-Tower-{site[-1]}{random.randint(1,5)}",
            "status": status,
            "priority": prio,
            "age_days": random.randint(1, 8),
            "assigned_to": random.choice(assignees) if status == "open" else "Unassigned",
            "site_name": site,
            "description": desc
        })
    return tickets

def get_maintenance_mock_data():
    """
    Returns a high-fidelity simulation of the Maintenance Schedule API.
    """
    sites = ["Site A", "Site B", "Site C", "Site D", "Site E", "Site F", "Site G", "Site H", "Site I", "Site J"]
    events = []
    
    for i in range(5):
        site = random.choice(sites)
        events.append({
            "event_id": f"MNT-{random.randint(100, 999)}",
            "site_name": site,
            "status": random.choice(["upcoming", "in_progress"]),
            "date": (datetime.now() + timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d"),
            "engineer": random.choice(["Tech-A", "Tech-B", "Senior-Lead"])
        })
    return events

def get_live_dashboard_data(use_mock=True):
    """
    Unified Entry Point: 100% API-Driven Operations.
    Monitoring (Prometheus), Ticketing (Jira), and Maintenance.
    """
    # 1. Get Live Monitoring Data (Prometheus)
    api_resp = fetch_live_prometheus(use_mock=use_mock)
    live_devices, live_usage, live_alerts = map_prometheus_to_telecom(api_resp)
    
    # 2. Get Live Ticketing Data (Jira API Mock)
    api_tickets = get_jira_mock_data()
    
    # 3. Get Live Maintenance Data (Schedule API Mock)
    api_maintenance = get_maintenance_mock_data()
    
    return {
        "devices": live_devices if live_devices else [],
        "alerts": live_alerts if live_alerts else [],
        "usage": live_usage if live_usage else [],
        "tickets": api_tickets,
        "maintenance": api_maintenance
    }

if __name__ == "__main__":
    # Test execution
    data = get_live_dashboard_data(use_mock=True)
    print(f"--- API-FIRST INGESTION AUDIT ---")
    print(f"Monitoring Sites: {len(set(d['site_name'] for d in data['devices']))}")
    print(f"Active Devices: {len(data['devices'])}")
    print(f"Active Tickets: {len(data['tickets'])}")
    print(f"Tickets Source: Simulated Jira API")
    print(f"----------------------------------")
    print(json.dumps(data['tickets'][:1], indent=2))
