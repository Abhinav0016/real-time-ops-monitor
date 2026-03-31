import os
import pandas as pd
from datetime import datetime
from openai import OpenAI
import random
import re
from rag_engine import retrieve_mixed, format_context
from query_builder import build_query
from dotenv import load_dotenv

load_dotenv()

def get_all_data(role="Fleet Operations Manager"):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "datasetss")
    devices = pd.read_csv(os.path.join(DATA_DIR, "devices_v2.csv"))
    alerts = pd.read_csv(os.path.join(DATA_DIR, "alerts_v2.csv"))
    usage = pd.read_csv(os.path.join(DATA_DIR, "usage.csv"))
    tickets = pd.read_csv(os.path.join(DATA_DIR, "tickets.csv"))

    # ... (rest of data processing remains the same until prompt) ...
    # Skip for brevity in this thought, but implementation will keep full context
    # actually I need to provide the full replacement content as requested by the tool rules if it's a single block

    # I'll replace from the start of the function to the start of generate_briefing_with_ai

    TYPES = ['Outage System', 'Tower', 'Network Node', 'Satellite Terminal', 'Bandwidth System', 'Latency Monitor']
    DEVICE_TYPES = {
        f"STL-{i:03d}": TYPES[i % 6] for i in range(1, 50)
    }

    # Map Site locations from CSV
    SITE_LOCATIONS = {}
    for _, row in devices.iterrows():
        if row['site'] not in SITE_LOCATIONS and 'latitude' in row and 'longitude' in row:
            SITE_LOCATIONS[row['site']] = {"lat": row['latitude'], "lon": row['longitude']}

    alert_counts = alerts.groupby('device_id').size()

    critical_issues = []
    now = datetime.now()

    for device, count in alert_counts.items():
        if count >= 3:
            dtype = DEVICE_TYPES.get(device, 'Unknown')
            site = devices[devices['device_id'] == device]['site'].iloc[0] if not devices[devices['device_id'] == device].empty else 'Unknown'
            critical_issues.append(f"{device} ({dtype}) has {count} alerts at Site {site} in last 24 hours")

    offline_devices = []

    for _, row in devices.iterrows():
        if row['status'] == 'offline':
            try:
                last_seen = pd.to_datetime(row['last_seen'], format='%d-%m-%Y %H:%M')
                hours_offline = int((now - last_seen).total_seconds() / 3600)
                duration = f"{hours_offline} hours"
            except Exception:
                duration = "unknown time"
            dtype = DEVICE_TYPES.get(row['device_id'], 'Unknown')
            offline_devices.append(f"{row['device_id']} ({dtype}) is offline at Site {row['site']} for {duration}")

    trending_issues = []

    for device in usage['device_id'].unique():
        dev_data = usage[usage['device_id'] == device]
        data = dev_data['data_used_gb'].values
        dates = dev_data['date'].values
        
        if len(data) >= 3:
            dtype = DEVICE_TYPES.get(device, 'Unknown')
            site = devices[devices['device_id'] == device]['site'].iloc[0] if not devices[devices['device_id'] == device].empty else 'Unknown'
            
            if data[-1] >= 60:
                trending_issues.append(f"{device} ({dtype}) at Site {site} is operating near critical capacity bounds (URGENT)")
            elif data[-1] > data[-2] > data[-3] and data[-1] > 45:
                pct_increase = ((data[-1] - data[-2]) / data[-2]) * 100
                if pct_increase > 20:
                    trending_issues.append(f"{device} ({dtype}) at Site {site} usage increased by {pct_increase:.1f}% on {dates[-1]}")

    ticket_issues = []

    for _, row in tickets.iterrows():
        if row['status'] == 'open' and row['days_open'] > 4:
            dtype = DEVICE_TYPES.get(row['device_id'], 'Unknown')
            site = devices[devices['device_id'] == row['device_id']]['site'].iloc[0] if not devices[devices['device_id'] == row['device_id']].empty else 'Unknown'
            ticket_issues.append(f"{row['device_id']} ({dtype}) at Site {site} has unresolved ticket {row['ticket_id']} (delayed {row['days_open']} days)")

    combined_critical = offline_devices[:2] + critical_issues[:2]
    if len(combined_critical) < 4:
        combined_critical = (offline_devices + critical_issues)[:4]

    trending_final = trending_issues[:4]
    issues_final = ticket_issues[:4]

    site_health = {}
    for site in SITE_LOCATIONS:
        site_health[site] = {"color": "green", "reason": "No major issues"}

    for item in combined_critical:
        match = re.search(r'Site ([A-Z])', item)
        if match:
            s = match.group(1)
            site_health[s]["color"] = "red"
            if "offline" in item.lower():
                site_health[s]["reason"] = "Critical: Device offline"
            else:
                site_health[s]["reason"] = "Critical: High alert volume"

    for item in trending_final + issues_final:
        match = re.search(r'Site ([A-Z])', item)
        if match:
            s = match.group(1)
            if site_health[s]["color"] == "green":
                site_health[s]["color"] = "orange"
                if "usage" in item.lower():
                    site_health[s]["reason"] = "Warning: Usage trending high"
                else:
                    site_health[s]["reason"] = "Warning: Outstanding resolution ticket"

    site_stats = []
    for device in usage['device_id'].unique():
        dev_data = usage[usage['device_id'] == device]
        s_rows = devices[devices['device_id'] == device]['site']
        site = s_rows.iloc[0] if not s_rows.empty else 'Unknown'
        last_usage = int(dev_data['data_used_gb'].iloc[-1]) if not dev_data.empty else 0
        site_stats.append({
            "site": site,
            "usage": last_usage,
            "cost": last_usage * 2,
            "revenue": last_usage * 5,
            "profit": last_usage * 3
        })
    site_stats.sort(key=lambda x: x["usage"], reverse=True)

    trend_data = []
    for date in sorted(usage['date'].unique()):
        day_data = usage[usage['date'] == date]
        trend_data.append({
            "date": date[-5:], 
            "Network Total": int(day_data['data_used_gb'].sum()),
            "Site H": int(day_data[day_data['device_id'] == 'STL-008']['data_used_gb'].sum()),
            "Site N": int(day_data[day_data['device_id'] == 'STL-014']['data_used_gb'].sum()),
            "Site E": int(day_data[day_data['device_id'] == 'STL-005']['data_used_gb'].sum())
        })

    results = {
        "critical": combined_critical,
        "trending": trending_issues[:4],
        "issues": ticket_issues[:4],
        "site_locations": SITE_LOCATIONS,
        "site_health": site_health,
        "stats": {
            "total_devices": len(devices),
            "online_devices": len(devices[devices['status'] == 'online']),
            "critical_alerts_count": len(critical_issues),
            "open_tickets_count": len(tickets[tickets['status'] == 'open'])
        },
        "charts": {
            "site_stats": site_stats,
            "trend_data": trend_data
        }
    }

    if not results["critical"] and not results["trending"] and not results["issues"]:
        results["all_clear"] = ["All systems normal"]
    else:
        results["all_clear"] = []

    # ── RAG Layer (Improvements 1–5 applied) ───────────────────────────────
    rag_query      = build_query(results)              # structured → query
    print(f"[RAG] Query built: '{rag_query}'")
    retrieved_docs = retrieve_mixed(rag_query)         # balanced: 1 SOP + 2 incidents
    print(f"[RAG] Retrieved {len(retrieved_docs)} docs: {[d.get('type') for d in retrieved_docs]}")
    context_block  = format_context(retrieved_docs)    # [SOP]/[HISTORY] tagged string
    print(f"[RAG] Context block ({len(context_block)} chars) ready for LLM")
    results["retrieved_context"] = retrieved_docs      # full dicts exposed in API
    # ───────────────────────────────────────────────────────────────────

    # Switch to Groq (Free & High Quota) using the OpenAI client
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ.get("GROQ_API_KEY")
    )

    # Specialized instructions for different roles
    # Specialized instructions for different roles
    role_instructions = {
        "Fleet Operations Manager": """
Focus on:
* Overall network uptime
* Region/site performance
* Business impact and cost implications
* Strategic resource allocation

Structure output EXACTLY with these sections:
🚨 Needs Immediate Attention:
(List critical device outages or high alert volumes)

📈 Trending Issues:
(Analyze usage trends and capacity risks using historical data)

⚠️ Other Issues:
(List details about unsolved tickets, stale resolutions, or minor alerts)

✅ Summary:
(Overall system health statement)

💡 Recommended Actions:
(Strategic steps for management)
""",
        "NOC Analyst": """
Focus on:
* Device-level failures and technical alerts
* Latency and connectivity root causes
* Technical troubleshooting steps

Structure output EXACTLY with these sections:
🚨 Needs Immediate Attention:
(List specific device IDs and technical failure details)

⚠️ Active Alerts:
(List ongoing warnings or recurring latency issues)

📈 Technical Trends:
(Analyze data usage spikes and historical performance)

✅ Summary:
(Status of the network intelligence layer)

💡 Recommended Actions:
(Technical steps for remediation)
""",
        "Site Supervisor": """
Focus on:
* Physical site issues and hardware condition
* Power status/battery levels and maintenance tasks
* Immediate on-site actions required

Structure output EXACTLY with these sections:
🚨 Site Issues:
(List physical site alerts or power failures)

⚠️ Hardware Status:
(Status of towers and satellite terminals)

📈 Usage Trends:
(Site-specific data demand)

✅ Summary:
(Current site operational stability)

💡 Recommended Actions:
(On-site maintenance steps)
"""
    }

    selected_instruction = role_instructions.get(role, "Generate a concise operational briefing.")

    prompt = f"""
You are an AI-powered telecom network operations assistant.
Your task is to generate a daily operations briefing for the user role: {role}.

DATA FOR ANALYSIS (Live Data):
{results}

RELEVANT KNOWLEDGE (SOP/HISTORY/RAG):
{context_block}

FORMATTING RULES (CRITICAL):
1. Use ONLY these emojis for headers: 🚨, 📈, ⚠️, 💰, ✅, 💡.
2. Every list item MUST start with a hyphen and a space: "- "
3. Every recommendation MUST follow this sequence:
   - First, describes the specific problem or status line starting with "- "
   - Then, provide the recommended action starting with "Action: " on the very next line.
   - Example:
     - STL-001 is offline at Site A for 12 hours.
     Action: Restart the device...
4. DO NOT provide an "Action: " line without a preceding "- " description text.
5. Historical references should start with "↳ " on a new line beneath the relevant item.
6. IMPORTANT: You MUST include specific numbers and historical data from the 'charts' and 'stats' provided in your analysis to justify trends.
7. Do not include any preamble or "OUTPUT" headers. Just provide the structured briefing starting with the first header.

Instructions for this specific role:
{selected_instruction}
"""

    def generate_briefing_with_ai(prompt):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b", # User requested specific OSS model
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            print(f"[LLM] ✅ OpenAI response received successfully. Length: {len(response.choices[0].message.content)}")
            print(f"DEBUG LLM OUTPUT:\n{response.choices[0].message.content}\n---")
            results["briefing_mode"] = "llm"
            return response.choices[0].message.content
        except Exception as e:
            print(f"[LLM] ❌ OpenAI API call failed: {type(e).__name__}: {e}")
            print("[LLM] ⚠️  Switching to RAG-informed fallback generator")
            results["briefing_mode"] = "fallback"
            
            # ── RAG-Aware Fallback ────────────────────────────────────────────────
            # Pull SOP and incident docs from what RAG already retrieved
            sop_docs = [d for d in retrieved_docs if d.get("type") == "sop"]
            inc_docs = [d for d in retrieved_docs if d.get("type") == "incident"]

            # Build action text from SOP, truncated to keep it readable
            def rag_action(item_text, is_high=False, is_med=False):
                if sop_docs:
                    sop_text = sop_docs[0]["text"]
                    # Try to find a SOP that mentions the device type
                    for sop in sop_docs:
                        for dtype in ['Satellite Terminal','Network Node','Tower',
                                      'Bandwidth System','Latency Monitor','Outage System']:
                            if dtype.lower() in sop.get("text","").lower() and f"({dtype})" in item_text:
                                sop_text = sop["text"]
                                break
                    action_src = sop_text.rstrip()
                else:
                    action_src = "Escalate to Tier 2 field operations immediately."

                prefix = "URGENT" if is_high else "MODERATE" if is_med else "ADVISORY"
                return f"Action: [{prefix}] {action_src}"

            # Build incident history note (shown on its own line, not inline)
            inc_note = ""
            inc_subline = ""
            if inc_docs:
                inc_subline = f"  ↳ Historical ref: {inc_docs[0]['text']}"

            fallback = "🔥 Top Priorities:\n"
            top_items = (results.get('critical', []) or results.get('trending', []))[:2]
            if top_items:
                for item in top_items:
                    fallback += f"- {item}\n"
                    if inc_subline:
                        fallback += f"{inc_subline}\n"
                    match_off = re.search(r'for (\d+) hours', item)
                    match_al  = re.search(r'has (\d+) alerts', item)
                    is_high   = (match_off and int(match_off.group(1)) > 12) or \
                                (match_al  and int(match_al.group(1))  >= 4)
                    is_med    = not is_high
                    fallback += "  " + rag_action(item, is_high, is_med) + "\n"
            else:
                fallback += "- No top-priority issues detected\n"

            fallback += "\n🚨 Needs Immediate Attention:\n"
            if not results.get('critical'):
                fallback += "- No issues detected\n"
            else:
                for item in results.get('critical', []):
                    fallback += f"- {item}\n"
                    if inc_subline:
                        fallback += f"{inc_subline}\n"
                    match_off = re.search(r'for (\d+) hours', item)
                    match_al  = re.search(r'has (\d+) alerts', item)
                    is_high   = (match_off and int(match_off.group(1)) > 12) or \
                                (match_al  and int(match_al.group(1))  >= 4)
                    is_med    = not is_high
                    fallback += "  " + rag_action(item, is_high, is_med) + "\n"

            fallback += "\n📈 Trending Issues:\n"
            if not results.get('trending'):
                fallback += "- No issues detected\n"
            else:
                for item in results.get('trending', []):
                    fallback += f"- {item}\n"
                    if inc_subline:
                        fallback += f"{inc_subline}\n"
                    fallback += "  " + rag_action(item, is_high=False, is_med=True) + "\n"

            fallback += "\n⚠️ Other Issues:\n"
            if not results.get('issues'):
                fallback += "- No issues detected\n"
            else:
                for item in results.get('issues', []):
                    fallback += f"- {item}\n"
                    if inc_subline:
                        fallback += f"{inc_subline}\n"
                    fallback += "  " + rag_action(item, is_high=False, is_med=True) + "\n"

            fallback += "\n💡 Recommended Actions:\n"
            if sop_docs:
                fallback += f"- Per SOP: {sop_docs[0]['text']}\n"
            if inc_docs:
                fallback += f"- Historical note: {inc_docs[0]['text']}\n"

            fallback += "\n✅ Summary:\n"
            if results.get('all_clear'):
                fallback += "- All systems nominal. No active issues detected.\n"
            else:
                fallback += "- Field operations should prioritise RED-status sites. " \
                            "Actions above are SOP-informed based on retrieved knowledge base.\n"

            return fallback

    briefing = generate_briefing_with_ai(prompt)
    return {"results": results, "briefing": briefing}

if __name__ == "__main__":
    print(get_all_data()["briefing"])