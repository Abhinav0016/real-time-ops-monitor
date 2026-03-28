import json
import requests
import random
from datetime import datetime, timedelta

# Public Prometheus Demo URL (for documentation/reference)
PROM_DEMO_URL = "https://prometheus.demo.do.prometheus.io/api/v1/query"

def get_prometheus_mock_data():
    """
    Returns a high-fidelity simulation of the Prometheus Query API response.
    This mimics the exact structure returned by /api/v1/query.
    """
    ts = datetime.utcnow().timestamp()
    return {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": [
                {
                    "metric": {"__name__": "up", "instance": "Cell-Tower-A1", "site": "Site A", "job": "telecom_nodes"},
                    "value": [ts, "1"]
                },
                {
                    "metric": {"__name__": "up", "instance": "Cell-Tower-A2", "site": "Site A", "job": "telecom_nodes"},
                    "value": [ts, "0"]
                },
                {
                    "metric": {"__name__": "up", "instance": "Cell-Tower-B1", "site": "Site B", "job": "telecom_nodes"},
                    "value": [ts, "1"]
                },
                {
                    "metric": {"__name__": "node_load1", "instance": "Cell-Tower-B1", "site": "Site B"},
                    "value": [ts, str(round(random.uniform(0.8, 2.2), 2))]
                },
                {
                    "metric": {"__name__": "alert_critical", "instance": "Cell-Tower-A2", "site": "Site A", "alert_type": "Signal Loss"},
                    "value": [ts, "1"]
                }
            ]
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
    
    device_health = []
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
            device_health.append({
                "device_id": f"PROM-{instance}",
                "site_name": site,
                "status": status,
                "timestamp": timestamp
            })
            
        # 2. Map 'node_load' or similar to usage
        if metric.get("__name__") == "node_load1":
            usage_gb = float(val_str) * 10 # Scale for dashboard visibility
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
                "device_id": instance,
                "site_name": site,
                "severity": severity,
                "message": f"Live Prometheus {severity.upper()} Alert: {metric.get('alert_type','General Error')}"
            })
            
    return device_health, usage_data, alerts

def get_live_dashboard_data(use_mock=True):
    """
    Entry point for the Dashboard 'Live Mode'.
    Combines Prometheus monitoring with existing local Tickets/Maintenance.
    """
    from ingestion import load_all_data
    
    # 1. Get Live Monitoring Data
    api_resp = fetch_live_prometheus(use_mock=use_mock)
    live_health, live_usage, live_alerts = map_prometheus_to_telecom(api_resp)
    
    # 2. Re-use existing local Tickets & Maintenance (static/manual entry systems)
    local_data = load_all_data()
    
    return {
        "device_health": live_health if live_health else local_data.get("devices",[]),
        "alerts": live_alerts if live_alerts else local_data.get("alerts",[]),
        "usage": live_usage if live_usage else local_data.get("usage",[]),
        "tickets": local_data["tickets"],
        "maintenance": local_data["maintenance"]
    }

if __name__ == "__main__":
    # Test execution
    data = get_live_dashboard_data(use_mock=True)
    print(f"Fetched {len(data['device_health'])} devices from Prometheus Mock")
    print(json.dumps(data['device_health'][:2], indent=2))
