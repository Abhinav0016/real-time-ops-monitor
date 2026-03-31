import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from detection import get_all_data
import rag_engine
from chatbot import get_chatbot_response

load_dotenv()

app = Flask(__name__)
CORS(app)

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'alerts@telecom-ops.ai')
SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(__file__), 'subscriptions.json')

# ── Pre-warm FAISS index at startup ──
print("[RAG] Building FAISS index from knowledge base...")
try:
    rag_engine.build_faiss_index()
    print(f"[RAG] Index ready — {rag_engine.get_index_size()} documents indexed.")
except Exception as e:
    print(f"[RAG] Error building index: {e}")

def send_alert_email(to_email, critical_alerts):
    if os.getenv('DISABLE_SENDGRID') == 'true':
        print(f"Skipping email for {to_email} (SendGrid disabled by admin)")
        return
        
    if not SENDGRID_API_KEY:
        print("SendGrid Error: API key not found in .env")
        return
    
    alert_text = "\n".join([f"- {alert}" for alert in critical_alerts])
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=to_email,
        subject='CRITICAL NETWORK ALERT',
        plain_text_content=f"Critical alerts detected in the network:\n\n{alert_text}\n\nPlease check the dashboard for more details."
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent to {to_email}: {response.status_code}")
    except Exception as e:
        print(f"SendGrid Error for {to_email}: {str(e)}")
        if "403" in str(e):
            print(f"HINT: Ensure '{SENDER_EMAIL}' is a verified sender in your SendGrid dashboard.")


@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.json
        email = data.get('email')
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        subscriptions = []
        if os.path.exists(SUBSCRIPTIONS_FILE):
            with open(SUBSCRIPTIONS_FILE, 'r') as f:
                try:
                    subscriptions = json.load(f)
                except json.JSONDecodeError:
                    subscriptions = []
        
        if email not in subscriptions:
            subscriptions.append(email)
            with open(SUBSCRIPTIONS_FILE, 'w') as f:
                json.dump(subscriptions, f, indent=4)
        
        return jsonify({"message": "Subscribed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/briefing', methods=['GET'])
def briefing():
    """Main endpoint: returns detected issues, site health, and AI briefing."""
    try:
        role = request.args.get('role', 'Fleet Operations Manager')
        data = get_all_data(role=role)
        
        # Check for critical alerts and notify subscribers
        results = data.get('results', {})
        critical_alerts = results.get('critical', [])
        
        if critical_alerts and os.path.exists(SUBSCRIPTIONS_FILE):
            with open(SUBSCRIPTIONS_FILE, 'r') as f:
                try:
                    subscribers = json.load(f)
                except json.JSONDecodeError:
                    subscribers = []
            
            for email in subscribers:
                send_alert_email(email, critical_alerts)
                
        return jsonify(data)
    except Exception as e:
        print(f"Error in briefing: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/rag-status', methods=['GET'])
def rag_status():
    """Debug endpoint: returns RAG index size and a sample query result."""
    try:
        sample_docs = rag_engine.retrieve("device offline connectivity loss escalate", k=3)
        return jsonify({
            "index_size": rag_engine.get_index_size(),
            "sample_query": "device offline connectivity loss escalate",
            "sample_retrieved": sample_docs
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        req_data = request.json
        message = req_data.get('message')
        role = req_data.get('role', 'Fleet Operations Manager')
        
        ops_data = get_all_data(role=role)
        processed_insights = ops_data.get('results', {})
        
        response = get_chatbot_response(message, role, processed_insights)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

