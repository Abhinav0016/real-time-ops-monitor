import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def format_input_for_llm(data, metrics):
    """
    Converts structured operational data into a concise text format for the LLM.
    """
    top_priorities = data.get('top_priorities', [])
    all_issues = data.get('all_issues', [])
    predictions = data.get('predictions', [])
    recommendations = data.get('recommendations', [])
    
    formatted = "=== CURRENT OPERATIONAL STATUS ===\n\n"
    
    formatted += "TOP PRIORITIES:\n"
    for issue in top_priorities:
        site_str = f" at {issue['site']}" if issue.get('site') else ""
        formatted += f"- {issue['type'].replace('_', ' ').title()}{site_str}: {issue['description']} (Priority: {issue['priority_score']})\n"
        formatted += f"  Impact: {issue.get('affected_devices', 0)} devices, {issue.get('related_tickets', 0)} tickets\n"
        
    formatted += "\nPREDICTIONS:\n"
    for pred in predictions:
        formatted += f"- {pred['type'].replace('_', ' ').upper()}: {pred['message']} (Confidence: {pred['confidence']})\n"
        
    formatted += "\nRECOMMENDED ACTIONS:\n"
    for rec in recommendations:
        formatted += f"- {rec['issue_type'].replace('_', ' ').title()}: {rec['action']}\n"
        
    formatted += f"\nGLOBAL KPIs:\n"
    g = metrics.get('global_metrics', {})
    formatted += f"- Total Sites: {g.get('total_sites', 0)}\n"
    formatted += f"- Total Devices: {g.get('total_devices', 0)}\n"
    formatted += f"- Total Offline: {g.get('total_offline_devices', 0)}\n"
    formatted += f"- Open Tickets: {g.get('total_open_tickets', 0)}\n"
    
    return formatted

def generate_prompt(formatted_input, role):
    """
    Generates a tailored prompt for the LLM based on the user's role.
    """
    role_instructions = {
        "Fleet Manager": "As a Fleet Manager, focus on device uptime, regional impact, and cost-effective maintenance. Use a professional and results-oriented tone.",
        "NOC Analyst": "As a NOC Analyst, focus on technical alerts, connectivity issues, and immediate troubleshooting steps. Use a precise and technical tone.",
        "Operations Head": "As an Operations Head, focus on high-level KPIs, business impact, and strategic risks. Use a concise and executive tone."
    }
    
    instruction = role_instructions.get(role, "Generate a concise operational briefing.")
    
    prompt = f"""
{instruction}

You are an AI Operations Assistant for a Telecom Network. 
Using the structured data provided below, generate a human-readable daily briefing.

STRUCTURE YOUR RESPONSE INTO THESE SECTIONS:
1. 🔥 Top Priorities (Highlights of the most critical issues)
2. 🚨 Needs Immediate Attention (Urgent technical failures)
3. 📈 Trending Issues (Problems that are developing)
4. 🔮 Predictions (Forward-looking risks)
5. 💡 Recommended Actions (Clear steps to take)
6. ✅ All Clear Summary (What parts of the network are healthy)

DATA INPUT:
{formatted_input}

Generate the briefing now:
"""
    return prompt

def call_llm(prompt, api_key=None):
    """
    Calls the Gemini API to generate the briefing.
    Dynamically finds the best available model to avoid 404 errors.
    """
    final_api_key = api_key or os.getenv('GOOGLE_API_KEY')

    if not final_api_key:
        print("Warning: No GOOGLE_API_KEY found. Using mock response.")
        return _mock_briefing()

    try:
        import google.generativeai as genai
        genai.configure(api_key=final_api_key)
        
        # Try to find an available model
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
        except Exception:
            # Fallback to common model names if listing fails
            available_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-1.0-pro']

        # Prioritize 1.5-flash, then 1.5-pro, then others
        target_models = []
        for pref in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash', 'gemini-1.0-pro']:
            for am in available_models:
                if pref in am:
                    target_models.append(am)
        
        # Add all other available models as final fallback
        target_models.extend([m for m in available_models if m not in target_models])

        last_error = "No supported models found."
        for model_name in target_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if hasattr(response, 'text') and response.text:
                    return response.text
            except Exception as e:
                last_error = str(e)
                continue
        
        return f"⚠️ Gemini API Error: {last_error}"

    except ImportError:
        raise RuntimeError("google-generativeai package not installed. Run: pip install google-generativeai")
    except Exception as e:
        raise RuntimeError(f"Unexpected Error: {e}")

def _mock_briefing():
    """Returns a static mock briefing when no API key is available."""
    return """[MOCK — No API Key Configured]

🔥 TOP PRIORITIES
- Multi-device outage at Site B. 3 devices offline. Priority Score: 5.

🚨 NEEDS IMMEDIATE ATTENTION
- Critical system alerts at Site B. High technical priority.

📈 TRENDING ISSUES
- Data usage spike detected. 22% increase over the last 24 hours.

🔮 PREDICTIONS
- High risk of data usage overflow if trends continue.
- High risk of SLA breach at Site A (ticket age: 5 days).

💡 RECOMMENDED ACTIONS
- Dispatch field technician to Site B.
- Escalate pending tickets at Site A.
- Optimize network bandwidth in affected region.

✅ ALL CLEAR SUMMARY
- 2 out of 3 sites showing stable connectivity.
- Maintenance schedules currently on track.
"""
        
def generate_briefing(data, metrics, role="Fleet Manager", api_key=None):
    """
    Orchestrates the AI briefing generation.
    """
    formatted_input = format_input_for_llm(data, metrics)
    prompt = generate_prompt(formatted_input, role)
    briefing_text = call_llm(prompt, api_key=api_key)
    
    return {
        "briefing_text": briefing_text
    }
