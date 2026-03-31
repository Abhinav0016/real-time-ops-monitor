import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_chatbot_response(message, role, processed_insights):
    system_prompt = f"""
You are a SPECIALIZED AI Telecom Network Operations Assistant embedded inside a dashboard.

Your goal is to provide BRIEF and EFFICIENT support strictly for this app.

Strict Domain Rules:
- ONLY answer questions related to telecom network operations, dashboard data, health alerts, and technical support for this specific platform.
- If a user asks a general-purpose or off-topic question (e.g., about recipes, general history, hobbies, or other unrelated domains), politely refuse and refocus them on the dashboard's operational data.
- Keep replies as short as possible while being informative.
- DO NOT use tables.
- Use single-level bullet points for list information.
- Adapt your response specifically for the user's ROLE: {role}.

Roles:
1. Fleet Manager → strategic, business impact, cost & uptime.
2. NOC Analyst → technical, device failures, alerts & root cause.
3. Site Supervisor → practical, on-site hardware & power issues.

Guidelines:
* Answer clearly and concisely.
* Provide direct, actionable insights.
* If possible, include: cause, impact, and recommended action as brief bullets.

Context Data:
{processed_insights}

Answer the user’s question briefly and efficiently, staying strictly within the operational domain.
"""

    try:
        # Using Groq with the user's requested model and parameters
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=1,
            max_completion_tokens=8192,
            top_p=1,
            stream=False 
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"I'm sorry, I'm having trouble processing your request via Groq. (Error: {str(e)})"
