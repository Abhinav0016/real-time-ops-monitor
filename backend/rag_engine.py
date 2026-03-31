"""
rag_engine.py — RAG Vector Store & Retrieval Engine
Loads rag_data.json, builds a FAISS index using sentence-transformers,
and exposes retrieve(), retrieve_mixed(), format_context(), and debug_retrieval().

Scope:
  - Semantic memory layer only (no real-time ingestion, no analytics)
  - Index is built ONCE on startup and held in memory
  - Top-K = 2-3 documents per query
"""

import json
import os
import numpy as np

# Module-level cache — populated once by build_faiss_index()
_index = None
_texts = None   # plain text list (for FAISS encoding)
_docs  = None   # full document dicts (for metadata-aware retrieval)
_model = None

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_KB_PATH = os.path.join(_BASE_DIR, "rag_data.json")


def _load_model():
    """Load the sentence-transformer embedding model (cached globally)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model


def load_knowledge_base():
    """Read rag_data.json and return list of document dicts."""
    with open(_KB_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)
    return docs


def build_faiss_index():
    """
    Encode all knowledge base texts and build a FAISS IndexFlatL2.
    Called once at app startup; results cached in module-level globals.

    Improvement 1: also caches full _docs list for metadata-aware retrieval.
    """
    global _index, _texts, _docs

    import faiss

    _docs  = load_knowledge_base()
    _texts = [doc["text"] for doc in _docs]

    model = _load_model()
    embeddings = model.encode(_texts, convert_to_numpy=True, normalize_embeddings=True)
    embeddings = embeddings.astype(np.float32)

    dim = embeddings.shape[1]       # 384 for all-MiniLM-L6-v2
    _index = faiss.IndexFlatL2(dim)
    _index.add(embeddings)

    return _index


# ── Improvement 1: retrieve() now returns full document dicts ──────────────

def retrieve(query: str, k: int = 3) -> list[dict]:
    """
    Semantic retrieval: given a plain-text query, return top-K relevant
    full document dicts from the knowledge base.

    Args:
        query: A natural-language search string derived from detected insights.
        k:     Number of documents to return (recommended: 2-3).

    Returns:
        List of k most relevant document dicts (with 'type', 'text', metadata).
    """
    global _index, _texts, _docs

    if _index is None or _texts is None:
        build_faiss_index()

    model = _load_model()
    query_vec = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    query_vec = query_vec.astype(np.float32)

    # Cap k at available document count
    k = min(k, len(_texts))
    distances, indices = _index.search(query_vec, k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(_docs):
            results.append(_docs[idx])   # Improvement 1: return full doc dict

    return results


def get_index_size() -> int:
    """Returns the number of vectors currently in the FAISS index."""
    if _index is None:
        return 0
    return _index.ntotal


# ── Improvement 3: format_context() ── tag docs for LLM clarity ───────────

def format_context(docs: list[dict]) -> str:
    """
    Convert retrieved document dicts into a tagged context string for the LLM.
    Helps the LLM distinguish SOPs (actions) from incidents (history).

    Tags:
        [SOP]     — standard operating procedure / recommended action
        [HISTORY] — past incident record
        [INFO]    — ticket or other context
    """
    context = ""
    for doc in docs:
        doc_type = doc.get("type", "info")
        text = doc.get("text", "")
        if doc_type == "sop":
            context += f"[SOP] {text}\n"
        elif doc_type == "incident":
            context += f"[HISTORY] {text}\n"
        else:
            context += f"[INFO] {text}\n"
    return context.strip()


# ── Improvement 5: retrieve_mixed() ── guaranteed type balance ────────────

def retrieve_mixed(query: str) -> list[dict]:
    """
    Fetch top-8 semantically similar docs, then enforce a balanced mix:
      - At least 1 SOP (recommended action)
      - At least 1 Incident (historical context)
      - Up to 3 total docs

    If primary search doesn't yield enough incidents, runs a secondary
    incident-biased sub-query to guarantee historical context appears.
    """
    candidates = retrieve(query, k=8)      # wider net than before

    sops      = [d for d in candidates if d.get("type") == "sop"]
    incidents = [d for d in candidates if d.get("type") == "incident"]

    # ── Secondary search if incidents are missing ──────────────────────────
    if len(incidents) < 1:
        # Build an incident-biased query to target historical records
        incident_query = _incident_bias_query(query)
        print(f"[RAG] No incidents in primary results — secondary search: '{incident_query}'")
        backup = retrieve(incident_query, k=5)
        extra_incidents = [d for d in backup
                           if d.get("type") == "incident" and d not in candidates]
        incidents += extra_incidents
        print(f"[RAG] Secondary search added {len(extra_incidents)} incident doc(s)")

    # Build the final balanced set: 1 SOP + up to 2 incidents
    mixed = sops[:1] + incidents[:2]

    # Pad to 3 with any remaining candidates if needed
    for doc in candidates:
        if len(mixed) >= 3:
            break
        if doc not in mixed:
            mixed.append(doc)

    return mixed


def _incident_bias_query(original_query: str) -> str:
    """
    Generate an incident-biased secondary query from the original.
    Appends historical keywords to shift FAISS results toward incident docs.
    """
    # Extract key topic words (first 4 meaningful words)
    stop = {"and", "or", "the", "a", "an", "to", "for", "in", "at", "on", "of"}
    topic_words = [w for w in original_query.split() if w.lower() not in stop][:4]
    topic = " ".join(topic_words)
    return f"{topic} past outage downtime history site failure incident"



# ── Improvement 6: debug_retrieval() ── query tuning helper ───────────────

def debug_retrieval(query: str) -> None:
    """
    Print ranked retrieval results for a given query.
    Use during development to verify retrieval quality and tune queries.
    """
    docs = retrieve(query, k=5)
    print(f"\n[DEBUG] Query: '{query}'")
    print(f"[DEBUG] Top {len(docs)} results:")
    for i, doc in enumerate(docs, 1):
        doc_type = doc.get("type", "?").upper()
        snippet  = doc.get("text", "")[:100].replace("\n", " ")
        print(f"  {i}. [{doc_type}] {snippet}...")
    print()
