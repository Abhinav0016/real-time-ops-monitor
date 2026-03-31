# 🚀 AI Telecom Network Operations Dashboard

An AI-powered decision intelligence system that transforms raw operational data into concise, role-based daily briefings and interactive assistance.

## 🧠 Overview

Modern telecom operations are overwhelmed by fragmented data. This dashboard centralizes device health, alerts, usage metrics, and tickets, using AI to prioritize what matters most for different organizational roles.

## 🎯 Key Features

- **Role-Based Daily Briefing**: Tailored summaries for Fleet Managers, NOC Analysts, and Site Supervisors.
- **Interactive AI Chatbot**: A domain-specific, role-aware assistant powered by Groq (LLM).
- **Proactive Root Cause Analysis**: AI-driven insights into "why" issues are happening and "what to do" about them.
- **Visual Analytics**: Interactive maps with pulsing critical alerts and performance trend charts.
- **Secure Integration**: Environment-based configuration for API keys.

## 🛠️ Tech Stack

- **Frontend**: React (Vite), Leaflet (Maps), Recharts (Analytics), Lucide-React (Icons), React-Markdown.
- **Backend**: Python, Flask, Groq API, OpenAI API (for briefings), Pandas (Data Processing), Python-Dotenv.

## 🚀 Getting Started

### Prerequisites

- Node.js & npm
- Python 3.8+
- Groq API Key & OpenAI API Key

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/armada-code-recet/code-warriors.git
   cd code-warriors
   ```

2. **Setup Backend**:
   ```bash
   # From root
   pip install -r requirements.txt
   ```
   Create a `.env` file in the `backend/` directory:
   ```env
   OPENAI_API_KEY=your_openai_key
   GROQ_API_KEY=your_groq_key
   ```

3. **Setup Frontend**:
   ```bash
   cd frontend
   npm install
   ```

### Running the App

1. **Start Backend**:
   ```bash
   cd backend
   python app.py
   ```
   (Runs on http://localhost:5000)

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   (Typically runs on http://localhost:3000)

## 📌 Usage

- **Switch Roles**: Use the selector in the top-right to view data as a Fleet Manager, NOC Analyst, or Site Supervisor.
- **Briefing**: The left panel automatically updates with a role-specific briefing.
- **Chatbot**: Use the floating widget in the bottom-right to ask specific operational questions. Use the "Typical Questions" chips for quick insights.

## 🧠 Contextual Awareness

The AI has access to:
- **Device Health**: Real-time status of all satellite terminals.
- **Alerts**: Severity-ranked event logs.
- **Usage**: Data trends and congestion risks.
- **Tickets**: Support backlog and escalation status.
