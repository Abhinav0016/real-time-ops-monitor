from datetime import datetime

def normalize_field(value, target_format=None):
    """
    Standardizes a field value based on the target format.
    - 'title': Title Case (e.g., 'Site A')
    - 'lower': lowercase (e.g., 'critical')
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    
    if isinstance(value, str):
        val = value.strip()
        if target_format == 'title':
            return val.title()
        elif target_format == 'lower':
            return val.lower()
    return value

def parse_timestamp(timestamp_str):
    """
    Parses a timestamp string into a datetime object.
    Supports ISO format and 'YYYY-MM-DD'.
    """
    if not timestamp_str:
        return None
    
    try:
        # Try ISO format (e.g., '2024-03-27T10:00:00Z')
        # Replacing 'Z' with +00:00 for fromisoformat if needed, but 3.11+ handles Z
        clean_ts = timestamp_str.replace('Z', '+00:00')
        return datetime.fromisoformat(clean_ts)
    except ValueError:
        try:
            # Try date-only format
            return datetime.strptime(timestamp_str, '%Y-%m-%d')
        except ValueError:
            return None

def normalize_data(data):
    """
    Cleans and standardizes the input data dictionary.
    """
    # 1. Normalize Devices
    for device in data.get('devices', []):
        device['site_name'] = normalize_field(device.get('site_name'), 'title')
        device['status'] = normalize_field(device.get('status'), 'lower')
        # Ensure status is either 'online' or 'offline'
        if device['status'] not in ['online', 'offline']:
            device['status'] = 'offline' # Default if invalid

    # 2. Normalize Alerts
    for alert in data.get('alerts', []):
        alert['severity'] = normalize_field(alert.get('severity'), 'lower')
        alert['timestamp_obj'] = parse_timestamp(alert.get('timestamp'))

    # 3. Normalize Usage
    for record in data.get('usage', []):
        record['region'] = normalize_field(record.get('region'), 'title')
        record['timestamp_obj'] = parse_timestamp(record.get('timestamp'))

    # 4. Normalize Tickets
    for ticket in data.get('tickets', []):
        ticket['site_name'] = normalize_field(ticket.get('site_name'), 'title')
        ticket['status'] = normalize_field(ticket.get('status'), 'lower')

    # 5. Normalize Maintenance
    for entry in data.get('maintenance', []):
        entry['site_name'] = normalize_field(entry.get('site_name'), 'title')
        entry['status'] = normalize_field(entry.get('status'), 'lower')
        entry['timestamp_obj'] = parse_timestamp(entry.get('date'))

    return data

def sort_chronologically(data_list):
    """Sorts a list of dictionaries by their 'timestamp_obj' field."""
    return sorted(data_list, key=lambda x: x.get('timestamp_obj') or datetime.min)

def group_by_site(records, site_field='site_name'):
    """Groups records by their site/location name."""
    grouped = {}
    for record in records:
        site = record.get(site_field) or "Unknown Site"
        if site not in grouped:
            grouped[site] = []
        grouped[site].append(record)
    return grouped

def preprocess_data(raw_data):
    """
    Main preprocessing orchestrator.
    - Normalizes fields.
    - Handles time parsing and sorting.
    - Groups data by site.
    - Calculates derived site summaries.
    """
    # 1. Normalize and parse timestamps
    clean_data = normalize_data(raw_data)

    # 2. Sort time-based data
    clean_data['alerts'] = sort_chronologically(clean_data.get('alerts', []))
    clean_data['usage'] = sort_chronologically(clean_data.get('usage', []))

    # 3. Create grouped structures
    devices_by_site = group_by_site(clean_data.get('devices', []))
    
    # To group alerts by site, we need to map device_id -> site_name
    device_to_site = {d['device_id']: d['site_name'] for d in clean_data.get('devices', []) if 'device_id' in d}
    
    alerts_by_site = {}
    for alert in clean_data.get('alerts', []):
        device_id = alert.get('device_id')
        site = device_to_site.get(device_id, "Unknown Site")
        if site not in alerts_by_site:
            alerts_by_site[site] = []
        alerts_by_site[site].append(alert)

    tickets_by_site = group_by_site(clean_data.get('tickets', []))
    usage_by_site = group_by_site(clean_data.get('usage', []), site_field='site_name')

    # 4. Calculate Site Summary (Derived Fields)
    site_summary = {}
    all_sites = set(devices_by_site.keys()) | set(alerts_by_site.keys()) | set(tickets_by_site.keys()) | set(usage_by_site.keys())
    
    for site in all_sites:
        site_devices = devices_by_site.get(site, [])
        total = len(site_devices)
        offline = sum(1 for d in site_devices if d.get('status') == 'offline')
        site_summary[site] = {
            "total_devices": total,
            "offline_devices": offline
        }

    # 5. Return structured object
    return {
        "devices_by_site": devices_by_site,
        "alerts_by_site": alerts_by_site,
        "tickets_by_site": tickets_by_site,
        "usage_by_site": usage_by_site,
        "usage": clean_data.get('usage', []),
        "maintenance": clean_data.get('maintenance', []),
        "site_summary": site_summary
    }

if __name__ == "__main__":
    # This part would typically import from ingestion in a real test script
    pass
