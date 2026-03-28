import json
import os

def normalize_site_name(site_name):
    """Standardizes site/location names (e.g., 'site a' -> 'Site A')."""
    if site_name:
        return site_name.strip().title()
    return site_name

def normalize_status(status):
    """Ensures status values are consistent lowercase ('online', 'offline')."""
    if status:
        return status.strip().lower()
    return status

def load_json_file(file_path, required_fields=None):
    """
    Helper function to load data from a JSON file and perform basic validation.
    
    Args:
        file_path (str): Path to the JSON file.
        required_fields (list): List of fields that must exist in each record.
        
    Returns:
        list: Data from the JSON file, or an empty list if loading fails.
    """
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} not found.")
        return []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            print(f"Warning: Data in {file_path} is not a list.")
            return []
            
        validated_data = []
        for record in data:
            if required_fields:
                missing = [field for field in required_fields if field not in record]
                if missing:
                    print(f"Warning: Missing required fields {missing} in record from {file_path}")
                    continue
            validated_data.append(record)
            
        return validated_data
            
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {file_path}: {e}")
        return []

def load_device_data(file_path='device_health.json'):
    """Loads and normalizes device health data."""
    required = ['device_id', 'status', 'site_name']
    data = load_json_file(file_path, required)
    
    for record in data:
        record['site_name'] = normalize_site_name(record.get('site_name'))
        record['status'] = normalize_status(record.get('status'))
        
    return data

def load_alerts(file_path='alerts.json'):
    """Loads and normalizes alerts data."""
    required = ['alert_id', 'device_id', 'severity']
    data = load_json_file(file_path, required)
    
    for record in data:
        # Normalization if needed (e.g., severity)
        record['severity'] = record.get('severity', '').strip().lower()
        
    return data

def load_usage(file_path='usage.json'):
    """Loads and normalizes usage data."""
    required = ['region', 'data_usage_gb', 'user_count']
    data = load_json_file(file_path, required)
    
    for record in data:
        record['region'] = normalize_site_name(record.get('region'))
        
    return data

def load_tickets(file_path='tickets.json'):
    """Loads and normalizes support ticket data."""
    required = ['ticket_id', 'status', 'site_name']
    data = load_json_file(file_path, required)
    
    for record in data:
        record['site_name'] = normalize_site_name(record.get('site_name'))
        record['status'] = normalize_status(record.get('status'))
        
    return data

def load_maintenance(file_path='maintenance.json'):
    """Loads and normalizes maintenance schedule data."""
    required = ['event_id', 'site_name', 'status']
    data = load_json_file(file_path, required)
    
    for record in data:
        record['site_name'] = normalize_site_name(record.get('site_name'))
        record['status'] = normalize_status(record.get('status'))
        
    return data

def load_all_data(data_dir='.'):
    """
    Aggregates data from all sources into a single structured dictionary.
    """
    return {
        "devices": load_device_data(os.path.join(data_dir, 'device_health.json')),
        "alerts": load_alerts(os.path.join(data_dir, 'alerts.json')),
        "usage": load_usage(os.path.join(data_dir, 'usage.json')),
        "tickets": load_tickets(os.path.join(data_dir, 'tickets.json')),
        "maintenance": load_maintenance(os.path.join(data_dir, 'maintenance.json'))
    }

if __name__ == "__main__":
    # Example usage
    all_data = load_all_data()
    print(json.dumps(all_data, indent=2))
