"""
query_builder.py — Insight-to-Query Translator
Converts the structured results dict from detection.py into a focused
semantic search string suitable for FAISS retrieval.

Design rules:
  - Prioritise signals in order: critical > trending > tickets
  - Keep query short and topic-focused (not a full sentence)
  - Never mix unrelated signals into one query; build richest signal-based query
"""

import re


def build_query(results: dict) -> str:
    """
    Translate detection results into a semantic query string for RAG retrieval.

    Priority order:
      1. Offline devices (critical)
      2. High-alert-count devices (critical)
      3. Usage trending spikes
      4. Stale open tickets

    Args:
        results: dict with keys 'critical', 'trending', 'issues', 'all_clear'

    Returns:
        A plain-text query string for rag_engine.retrieve()
    """
    critical = results.get("critical", [])
    trending = results.get("trending", [])
    issues   = results.get("issues", [])

    query_parts = []

    # --- Offline device signals ---
    offline_items = [c for c in critical if "offline" in c.lower()]
    if offline_items:
        # Check if long-duration offline (> 12 hours)
        long_offline = any(
            _extract_hours(item) > 12 for item in offline_items
        )
        if long_offline:
            query_parts.append("device offline extended downtime emergency field dispatch escalate")
        else:
            query_parts.append("device offline connectivity loss restart terminal site outage")

    # --- High-alert-count signals ---
    alert_items = [c for c in critical if "alerts" in c.lower()]
    if alert_items:
        # Check severity (4+ alerts = high, 3 = medium)
        high_alert = any(
            _extract_alert_count(item) >= 4 for item in alert_items
        )
        if high_alert:
            query_parts.append("high alert volume multiple failures cascading critical escalation")
        else:
            query_parts.append("repeated alerts device failure diagnosis connectivity issue")

    # --- Usage trend signals ---
    if trending:
        query_parts.append("data usage spike trending high bandwidth risk unauthorized access throttle")

    # --- Stale ticket signals ---
    if issues:
        long_stale = any(
            _extract_days(item) > 5 for item in issues
        )
        if long_stale:
            query_parts.append("open ticket unresolved stale SLA breach escalate senior operations")
        else:
            query_parts.append("open ticket pending field visit delayed resolution priority review")

    # --- All clear ---
    if results.get("all_clear") and not query_parts:
        return "nominal system operation no issues all devices online"

    # Join the most significant query terms (de-duplicate words, keep order)
    combined = " ".join(query_parts)
    return _deduplicate_words(combined)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_hours(text: str) -> int:
    """Extract 'for N hours' from an offline description."""
    match = re.search(r'for (\d+) hours', text)
    return int(match.group(1)) if match else 0


def _extract_alert_count(text: str) -> int:
    """Extract 'has N alerts' from an alert description."""
    match = re.search(r'has (\d+) alerts', text)
    return int(match.group(1)) if match else 0


def _extract_days(text: str) -> int:
    """Extract 'delayed N days' from a ticket description."""
    match = re.search(r'delayed (\d+) days', text)
    return int(match.group(1)) if match else 0


def _deduplicate_words(text: str) -> str:
    """Remove duplicate words while preserving order."""
    seen = set()
    result = []
    for word in text.split():
        if word not in seen:
            seen.add(word)
            result.append(word)
    return " ".join(result)


# ── Improvement 2: plain-text query builder (for generate_with_rag path) ──

def build_query_from_text(insights: str) -> str:
    """
    Convert a plain-text insights string into a semantic search query.
    Used by the generate_with_rag() integration path (Improvement 4).

    Unlike build_query() which takes a structured results dict, this accepts
    a raw string — useful for standalone RAG pipeline calls.

    Args:
        insights: Plain string describing detected issues.

    Returns:
        A semantic query string for rag_engine.retrieve().
    """
    insights = insights.lower()

    if "outage" in insights:
        return "site outage repeated failure connectivity issue"
    elif "offline" in insights and ("12" in insights or "20" in insights or "21" in insights):
        return "device offline extended downtime emergency field dispatch escalate"
    elif "offline" in insights:
        return "device offline instability repeated disconnection restart terminal"
    elif "usage" in insights or "bandwidth" in insights:
        return "data usage increasing trend limit risk unauthorized throttle"
    elif "alert" in insights and any(str(n) in insights for n in range(4, 10)):
        return "high alert volume multiple failures cascading critical escalation"
    elif "alert" in insights:
        return "repeated alerts device failure diagnosis connectivity issue"
    elif "ticket" in insights or "unresolved" in insights:
        return "open ticket unresolved stale SLA breach escalate priority review"
    else:
        return "network issue telecom operations monitoring"
