# 🚀 AI Telecom - Backend Service

This is the Flask backend for the Real-Time Ops Monitor. It handles data processing, RAG (Retrieval-Augmented Generation), and AI briefing generation.

## 🛠️ Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   Copy `.env.template` to `.env` and add your API keys:
   ```bash
   cp .env.template .env
   ```

3. **Required Keys**:
   - `GROQ_API_KEY`: Get from [Groq Console](https://console.groq.com/)
   - `OPENAI_API_KEY`: For briefing generation.

## 🚀 Running the Service

```bash
python app.py
```
The server will run on [http://localhost:5000](http://localhost:5000).

## 📂 Structure
- `datasetss/`: CSV data source.
- `app.py`: Flask entry point.
- `detection.py`: Core logic for issue detection.
- `rag_engine.py`: FAISS-based vector search.
