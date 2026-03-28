import streamlit as st
from datetime import date

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Daily Operations Briefing",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Design System CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {
    background: #080d14 !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stHeader"]        { background: transparent !important; }
[data-testid="stSidebar"]       { display: none !important; }
[data-testid="collapsedControl"]{ display: none !important; }
#MainMenu, footer, header       { visibility: hidden !important; }

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar            { width: 5px; }
::-webkit-scrollbar-track      { background: #0d1520; }
::-webkit-scrollbar-thumb      { background: #1e3a5f; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover{ background: #2563eb; }

/* ═══════════════════════════════
   STREAMLIT LAYOUT OVERRIDES
   Force columns to stretch evenly, remove default gaps
═══════════════════════════════ */
/* Zero out all the default margin Streamlit adds between widgets */
[data-testid="stVerticalBlock"] > div {
    gap: 0 !important;
}
/* Make column containers fill their parent height */
[data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 0 !important;
}
/* Remove the gap Streamlit adds between st.columns() groups */
[data-testid="stHorizontalBlock"] {
    gap: 12px !important;
    align-items: stretch !important;
}
/* Ensure the stMarkdown wrappers inside columns don't add extra space */
[data-testid="column"] > [data-testid="stMarkdownContainer"],
[data-testid="column"] > div > [data-testid="stMarkdownContainer"] {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}
/* Make cards inside equal-height rows stretch to fill the container */
[data-testid="column"] > div > div > div > .card,
[data-testid="column"] > div > .card {
    flex: 1 !important;
    margin-bottom: 0 !important;
}
/* Main column padding from streamlit */
[data-testid="stMainBlockContainer"] { padding: 0 !important; }
/* Remove the default top-padding streamlit adds */
.main > div:first-child, .block-container > div:first-child { padding-top: 0 !important; }
/* Expander tweaks */
[data-testid="stExpander"] {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
    overflow: hidden !important;
}
/* Remove spacing between the control bar selectors */
[data-testid="stSelectbox"], [data-testid="stDateInput"] { margin-bottom: 0 !important; padding-bottom: 0 !important; }


/* ═══════════════════════════════
   HEADER BAR
═══════════════════════════════ */
.noc-header {
    background: linear-gradient(135deg, #0f1923 0%, #111d2e 100%);
    border-bottom: 1px solid rgba(37,99,235,0.25);
    padding: 0 32px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
.noc-header-left {
    display: flex;
    align-items: center;
    gap: 14px;
}
.noc-logo {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #1d4ed8, #7c3aed);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    box-shadow: 0 4px 12px rgba(29,78,216,0.4);
}
.noc-title {
    font-size: 1.2rem; font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.02em;
}
.noc-subtitle {
    font-size: 0.78rem; color: #64748b;
    margin-top: 1px;
}
.noc-badge {
    background: rgba(37,99,235,0.15);
    border: 1px solid rgba(37,99,235,0.35);
    color: #60a5fa;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 500;
}
.live-dot {
    width: 8px; height: 8px;
    background: #22c55e;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px #22c55e;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ═══════════════════════════════
   CONTROL BAR
═══════════════════════════════ */
.control-strip {
    background: #0d1520;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: 12px 32px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.ctrl-label {
    font-size: 0.78rem; color: #64748b; font-weight: 500;
    white-space: nowrap;
}

/* ═══════════════════════════════
   MAIN WRAPPER
═══════════════════════════════ */
.noc-body {
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 0;
    min-height: calc(100vh - 116px);
}
.noc-left  { padding: 24px 20px 24px 32px; border-right: 1px solid rgba(255,255,255,0.05); }
.noc-right { padding: 24px 32px 24px 20px; background: rgba(255,255,255,0.01); }

/* ═══════════════════════════════
   CARD BASE
═══════════════════════════════ */
.card {
    background: linear-gradient(145deg, #111d2e 0%, #0e1928 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
    transition: border-color .2s, box-shadow .2s, transform .15s;
    box-shadow: 0 2px 16px rgba(0,0,0,0.25);
}
.card:hover {
    border-color: rgba(37,99,235,0.3);
    box-shadow: 0 4px 28px rgba(0,0,0,0.35);
    transform: translateY(-1px);
}
.card-sm { padding: 16px; }

/* Priority card — hero treatment */
.card-priority {
    background: linear-gradient(145deg, #12202f 0%, #0f1e30 100%);
    border: 1px solid rgba(239,68,68,0.25);
    box-shadow: 0 4px 24px rgba(239,68,68,0.08), 0 2px 12px rgba(0,0,0,0.3);
}
.card-priority:hover {
    border-color: rgba(239,68,68,0.45);
    box-shadow: 0 6px 32px rgba(239,68,68,0.14), 0 2px 16px rgba(0,0,0,0.4);
}

/* AI Briefing card glow */
.card-briefing {
    border: 1px solid rgba(99,102,241,0.3);
    box-shadow: 0 4px 24px rgba(99,102,241,0.1), 0 2px 12px rgba(0,0,0,0.3);
}
.card-briefing:hover {
    border-color: rgba(99,102,241,0.5);
    box-shadow: 0 6px 32px rgba(99,102,241,0.18), 0 2px 16px rgba(0,0,0,0.4);
}

/* ═══════════════════════════════
   CARD HEADER
═══════════════════════════════ */
.card-head {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.card-icon {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
}
.icon-red    { background: rgba(239,68,68,0.15); }
.icon-orange { background: rgba(249,115,22,0.15); }
.icon-yellow { background: rgba(234,179,8,0.15); }
.icon-green  { background: rgba(34,197,94,0.15); }
.icon-blue   { background: rgba(59,130,246,0.15); }
.icon-purple { background: rgba(139,92,246,0.15); }
.icon-teal   { background: rgba(20,184,166,0.15); }

.card-title {
    font-size: 0.92rem;
    font-weight: 600;
    color: #e2e8f0;
    letter-spacing: -0.01em;
}
.card-count {
    margin-left: auto;
    background: rgba(255,255,255,0.06);
    color: #94a3b8;
    font-size: 0.72rem;
    padding: 2px 8px;
    border-radius: 20px;
    font-weight: 500;
}

/* ═══════════════════════════════
   PRIORITY ITEMS
═══════════════════════════════ */
.prio-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    transition: background .15s;
}
.prio-item:last-child { border: none; padding-bottom: 0; }
.prio-num {
    width: 26px; height: 26px; flex-shrink: 0;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700;
    margin-top: 1px;
}
.num-1 { background: rgba(239,68,68,0.2);  color: #f87171; border: 1px solid rgba(239,68,68,0.4); }
.num-2 { background: rgba(249,115,22,0.2); color: #fb923c; border: 1px solid rgba(249,115,22,0.4); }
.num-3 { background: rgba(234,179,8,0.2);  color: #facc15; border: 1px solid rgba(234,179,8,0.4); }
.prio-body { flex: 1; min-width: 0; }
.prio-title { font-weight: 600; font-size: 0.88rem; line-height: 1.3; }
.prio-1 { color: #f87171; }
.prio-2 { color: #fb923c; }
.prio-3 { color: #facc15; }
.prio-meta { color: #64748b; font-size: 0.78rem; margin-top: 3px; line-height: 1.4; }
.sev-pill {
    display: inline-block;
    padding: 2px 8px; border-radius: 20px;
    font-size: 0.68rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: .04em;
    margin-top: 4px;
}
.sev-high   { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.sev-medium { background: rgba(249,115,22,0.15); color: #fb923c; border: 1px solid rgba(249,115,22,0.3); }
.sev-low    { background: rgba(34,197,94,0.15);  color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.score-chip {
    background: rgba(99,102,241,0.15); color: #a5b4fc;
    border: 1px solid rgba(99,102,241,0.3);
    padding: 2px 8px; border-radius: 20px;
    font-size: 0.68rem; font-weight: 600;
    white-space: nowrap;
    margin-top: 1px;
}

/* ═══════════════════════════════
   BULLET LIST ITEMS
═══════════════════════════════ */
.bul-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.85rem;
    color: #94a3b8;
    line-height: 1.5;
    transition: color .15s;
}
.bul-item:last-child { border: none; padding-bottom: 0; }
.bul-dot {
    width: 6px; height: 6px; border-radius: 50%;
    flex-shrink: 0; margin-top: 6px;
}
.dot-red    { background: #ef4444; box-shadow: 0 0 6px rgba(239,68,68,.5); }
.dot-orange { background: #f97316; box-shadow: 0 0 6px rgba(249,115,22,.5); }
.dot-green  { background: #22c55e; box-shadow: 0 0 6px rgba(34,197,94,.5); }
.dot-blue   { background: #3b82f6; box-shadow: 0 0 6px rgba(59,130,246,.5); }
.dot-purple { background: #8b5cf6; box-shadow: 0 0 6px rgba(139,92,246,.5); }
.bul-em { color: #e2e8f0; font-weight: 600; }
.bul-action { color: #fb923c; font-weight: 600; }
.bul-conf { color: #22c55e; font-size: 0.75rem; font-style: italic; }
.bul-conf-med { color: #facc15; font-size: 0.75rem; font-style: italic; }

/* ═══════════════════════════════
   STAT ROWS (RIGHT PANEL)
═══════════════════════════════ */
.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.stat-row:last-child { border: none; padding-bottom: 0; }
.stat-label { color: #64748b; font-size: 0.82rem; }
.stat-val   { font-weight: 700; font-size: 0.88rem; }
.val-green  { color: #4ade80; }
.val-red    { color: #f87171; }
.val-orange { color: #fb923c; }
.val-white  { color: #e2e8f0; }

/* Progress bar */
.prog-wrap { margin-top: 4px; }
.prog-bar-bg {
    background: rgba(255,255,255,0.07);
    border-radius: 99px; height: 5px; overflow: hidden;
}
.prog-bar-fill {
    height: 100%; border-radius: 99px;
    transition: width .8s cubic-bezier(.4,0,.2,1);
}
.fill-green  { background: linear-gradient(90deg, #22c55e, #4ade80); box-shadow: 0 0 8px rgba(34,197,94,.4); }
.fill-orange { background: linear-gradient(90deg, #f97316, #fb923c); box-shadow: 0 0 8px rgba(249,115,22,.4); }
.fill-red    { background: linear-gradient(90deg, #ef4444, #f87171); box-shadow: 0 0 8px rgba(239,68,68,.4); }
.fill-blue   { background: linear-gradient(90deg, #2563eb, #60a5fa); box-shadow: 0 0 8px rgba(37,99,235,.4); }

/* ═══════════════════════════════
   TICKET TABLE
═══════════════════════════════ */
.tkt-table { width: 100%; border-collapse: collapse; }
.tkt-table th {
    color: #475569; font-size: 0.72rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: .06em;
    padding: 0 10px 10px;
    text-align: left;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.tkt-table td {
    padding: 10px;
    color: #94a3b8;
    font-size: 0.82rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    transition: background .15s;
}
.tkt-table tr:last-child td { border: none; }
.tkt-table tr:hover td { background: rgba(255,255,255,0.03); color: #e2e8f0; }
.tkt-table td:first-child { color: #60a5fa; font-weight: 600; font-family: 'Courier New', monospace; }
.badge {
    display: inline-block; padding: 3px 9px;
    border-radius: 20px; font-size: 0.71rem; font-weight: 700;
    text-transform: capitalize; letter-spacing: .02em;
}
.b-critical { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,.3); }
.b-high     { background: rgba(249,115,22,0.15); color: #fb923c; border: 1px solid rgba(249,115,22,.3); }
.b-medium   { background: rgba(234,179,8,0.15);  color: #facc15; border: 1px solid rgba(234,179,8,.3); }
.b-low      { background: rgba(34,197,94,0.15);  color: #4ade80; border: 1px solid rgba(34,197,94,.3); }
.b-open     { background: rgba(59,130,246,0.12); color: #60a5fa; border: 1px solid rgba(59,130,246,.25); }
.b-pending  { background: rgba(234,179,8,0.12);  color: #facc15; border: 1px solid rgba(234,179,8,.25); }
.b-closed   { background: rgba(255,255,255,0.06);color: #64748b; border: 1px solid rgba(255,255,255,.1); }

/* ═══════════════════════════════
   AI BRIEFING TEXT
═══════════════════════════════ */
.briefing-text {
    font-size: 0.85rem;
    line-height: 2;
    color: #94a3b8;
    white-space: pre-wrap;
    font-family: 'Inter', sans-serif;
}
.briefing-text strong, .briefing-text b { color: #e2e8f0; }

/* ═══════════════════════════════
   SIDEBAR DIVIDER
═══════════════════════════════ */
.sidebar-head {
    font-size: 0.68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .1em;
    color: #334155;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

/* ═══════════════════════════════
   WELCOME SCREEN
═══════════════════════════════ */
.welcome {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 60vh;
    text-align: center;
    gap: 24px;
}
.welcome-glow {
    font-size: 3.5rem;
    filter: drop-shadow(0 0 24px rgba(37,99,235,.5));
}
.welcome h2 { font-size: 1.8rem; font-weight: 700; color: #f1f5f9; letter-spacing: -.03em; }
.welcome p  { color: #475569; font-size: 0.9rem; max-width: 420px; line-height: 1.7; }
.feat-grid {
    display: grid; grid-template-columns: repeat(3,1fr); gap: 16px;
    width: 100%; max-width: 480px;
}
.feat-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 16px 12px; text-align: center;
}
.feat-icon { font-size: 1.6rem; margin-bottom: 6px; }
.feat-label { color: #475569; font-size: 0.75rem; font-weight: 500; }

/* ═══════════════════════════════
   FOOTER
═══════════════════════════════ */
.noc-footer {
    background: #0d1520;
    border-top: 1px solid rgba(255,255,255,0.05);
    padding: 12px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.footer-text { color: #1e3a5f; font-size: 0.72rem; }

/* ── Streamlit widget overrides ── */
[data-testid="stSelectbox"] > div > div {
    background: #0f1923 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 0.85rem !important;
}
[data-testid="stSelectbox"] label { display: none !important; }

[data-testid="stDateInput"] > div > div > input {
    background: #0f1923 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 0.85rem !important;
}
[data-testid="stDateInput"] label { display: none !important; }

.stButton > button {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: -.01em !important;
    padding: 10px 20px !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
    transition: all .2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.5) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stSpinner"] { color: #3b82f6; }
.stExpander { background: transparent !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 10px !important; }
[data-testid="stExpanderDetails"] { background: #0a1220 !important; }
hr { border-color: rgba(255,255,255,0.06) !important; }
</style>
""", unsafe_allow_html=True)

# ─── Imports ─────────────────────────────────────────────────────────────────
from pipeline import generate_daily_briefing

# ─── Header ──────────────────────────────────────────────────────────────────
today_str = date.today().strftime("%B %d, %Y")
st.markdown(f"""
<div class="noc-header">
  <div class="noc-header-left">
    <div class="noc-logo">📡</div>
    <div>
      <div class="noc-title">AI Daily Operations Briefing</div>
      <div class="noc-subtitle">{today_str} &nbsp;·&nbsp; Telecom NOC Platform</div>
    </div>
    <div class="noc-badge">Enterprise</div>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <span class="live-dot"></span>
    <span style="color:#475569;font-size:.78rem;">Live</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Control Bar ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns([0.15, 1.1, 1.1, 1.2])
with c1:
    st.markdown('<div style="padding-top:8px"><span style="font-size:.78rem;color:#64748b;font-weight:500">Role</span></div>', unsafe_allow_html=True)
with c2:
    role = st.selectbox("Role", ("Fleet Manager", "NOC Analyst", "Operations Head"), key="role_sel")
with c3:
    selected_date = st.date_input("Date", value=date.today(), key="date_sel")
with c4:
    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
    gen_btn = st.button("⚡  Generate Briefing", use_container_width=True)

st.markdown('<hr style="margin:0">', unsafe_allow_html=True)

# ─── Helper Functions ─────────────────────────────────────────────────────────

def _sev_pill(sev):
    cls = {"high": "sev-high", "medium": "sev-medium", "low": "sev-low"}.get(sev, "sev-low")
    return f'<span class="sev-pill {cls}">{sev}</span>'

def _badge(text, cls):
    return f'<span class="badge {cls}">{text}</span>'

def _pct_bar(pct, color_cls):
    p = min(100, max(0, pct))
    return f'<div class="prog-wrap"><div class="prog-bar-bg"><div class="prog-bar-fill {color_cls}" style="width:{p}%"></div></div></div>'

def render_priorities(top):
    num_cls = ["num-1","num-2","num-3"]
    ptitle_cls = ["prio-1","prio-2","prio-3"]
    rows = ""
    for i, iss in enumerate(top[:3]):
        nc  = num_cls[i]  if i < 3 else "num-3"
        ptc = ptitle_cls[i] if i < 3 else "prio-3"
        title   = iss["type"].replace("_"," ").title()
        site    = f" · {iss['site']}" if iss.get("site") else ""
        desc    = iss.get("description","")[:90]
        sev     = iss.get("severity","medium")
        score   = iss.get("priority_score", 0)
        devs    = iss.get("affected_devices", 0)
        tkts    = iss.get("related_tickets", 0)
        rows += f"""
        <div class="prio-item">
          <div class="prio-num {nc}">{i+1}</div>
          <div class="prio-body">
            <div class="prio-title {ptc}">{title}{site}</div>
            <div class="prio-meta">{desc}</div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px;">
              {_sev_pill(sev)}
              <span class="score-chip">Score {score}</span>
              <span style="color:#475569;font-size:.72rem;align-self:center">{devs} devices · {tkts} tickets</span>
            </div>
          </div>
        </div>"""
    return f"""<div class="card card-priority">
      <div class="card-head">
        <div class="card-icon icon-red">🔥</div>
        <span class="card-title">Top Priorities Today</span>
        <span class="card-count">{len(top)} issues</span>
      </div>{rows}</div>"""

def render_attention(issues):
    high = [i for i in issues if i.get("severity") == "high"][:4]
    rows = ""
    for iss in high:
        title = iss["type"].replace("_"," ").title()
        site  = f" at {iss['site']}" if iss.get("site") else ""
        desc  = iss.get("description","")[:70]
        rows += f'<div class="bul-item"><div class="bul-dot dot-red"></div><div><span class="bul-em">{title}{site}</span> — <span class="bul-action">{desc}</span></div></div>'
    if not rows:
        rows = '<div class="bul-item"><div class="bul-dot dot-green"></div><span>No high-severity issues at this time.</span></div>'
    return f"""<div class="card">
      <div class="card-head"><div class="card-icon icon-orange">⚠️</div><span class="card-title">Needs Immediate Attention</span></div>
      {rows}</div>"""

def render_trending(issues):
    trending = [i for i in issues if i["type"] in ("usage_spike","site_degradation","unstable_device")][:4]
    rows = ""
    for iss in trending:
        title = iss["type"].replace("_"," ").title()
        desc  = iss.get("description","")[:72]
        rows += f'<div class="bul-item"><div class="bul-dot dot-orange"></div><div><span class="bul-em">{title}</span> — {desc}</div></div>'
    if not rows:
        rows = '<div class="bul-item"><div class="bul-dot dot-blue"></div><span>No significant trending issues detected.</span></div>'
    return f"""<div class="card" style="height:100%">
      <div class="card-head"><div class="card-icon icon-yellow">📈</div><span class="card-title">Trending Issues</span></div>
      {rows}</div>"""

def render_predictions(preds):
    rows = ""
    for p in preds:
        conf = p.get("confidence","medium")
        conf_cls = "bul-conf" if conf == "high" else "bul-conf-med"
        msg = p["message"][:80]
        rows += f'<div class="bul-item"><div class="bul-dot dot-purple"></div><div>{msg} <span class="{conf_cls}">({conf})</span></div></div>'
    if not rows:
        rows = '<div class="bul-item"><div class="bul-dot dot-green"></div><span>No risk predictions for today.</span></div>'
    return f"""<div class="card" style="height:100%">
      <div class="card-head"><div class="card-icon icon-purple">🔮</div><span class="card-title">Predictions</span></div>
      {rows}</div>"""

def render_changes(metrics):
    g = metrics.get("global_metrics",{})
    total = g.get("total_devices",0)
    offline = g.get("total_offline_devices",0)
    online_pct = round(((total-offline)/total*100) if total>0 else 100,1)
    crits = g.get("total_critical_alerts",0)
    tkts  = g.get("total_open_tickets",0)
    return f"""<div class="card" style="height:100%">
      <div class="card-head"><div class="card-icon icon-teal">📅</div><span class="card-title">System Changes</span></div>
      <div class="bul-item"><div class="bul-dot dot-green"></div><span>Uptime: <span class="bul-em">{online_pct}%</span> of devices operational ↑</span></div>
      <div class="bul-item"><div class="bul-dot dot-orange"></div><span>Alerts: <span class="bul-em">{crits} critical</span> active</span></div>
      <div class="bul-item"><div class="bul-dot dot-blue"></div><span>Open tickets: <span class="bul-em">{tkts}</span> pending resolution</span></div>
    </div>"""

def render_tickets(issues):
    rows_html = ""
    added = 0
    badge_map = {
        "critical": "b-critical","high":"b-high","medium":"b-medium","low":"b-low"
    }
    status_map = {"open":"b-open","pending":"b-pending","closed":"b-closed"}
    for iss in issues:
        for t in iss.get("linked_data",{}).get("tickets",[]):
            if added >= 6: break
            tid    = t.get("ticket_id","—")
            prio   = t.get("priority","low").lower()
            status = t.get("status","open").lower()
            asgn   = t.get("assigned_to","Unassigned")
            age    = t.get("age_days","—")
            pb = _badge(prio, badge_map.get(prio,"b-low"))
            sb = _badge(status, status_map.get(status,"b-open"))
            rows_html += f"<tr><td>{tid}</td><td>{pb}</td><td>{sb}</td><td>{asgn}</td><td>{age}d</td></tr>"
            added += 1
    if not rows_html:
        rows_html = "<tr><td colspan='5' style='text-align:center;color:#334155;padding:20px'>No linked tickets</td></tr>"
    return f"""<div class="card" style="height:100%">
      <div class="card-head"><div class="card-icon icon-blue">📋</div><span class="card-title">Open Tickets</span></div>
      <table class="tkt-table">
        <thead><tr><th>ID</th><th>Priority</th><th>Status</th><th>Assigned</th><th>Age</th></tr></thead>
        <tbody>{rows_html}</tbody>
      </table></div>"""

def render_all_clear(issues):
    hi = [i for i in issues if i.get("severity")=="high"]
    ok = len(issues)-len(hi)
    rows = '<div class="bul-item"><div class="bul-dot dot-green"></div>No safety incidents reported.</div>'
    rows += f'<div class="bul-item"><div class="bul-dot dot-green"></div><span><span class="bul-em">{ok}</span> issues within acceptable parameters.</span></div>'
    if not hi:
        rows += '<div class="bul-item"><div class="bul-dot dot-green"></div>All monitored sites reachable.</div>'
    return f"""<div class="card">
      <div class="card-head"><div class="card-icon icon-green">✅</div><span class="card-title">All Clear</span></div>
      {rows}</div>"""

def render_snapshot(metrics):
    g = metrics.get("global_metrics",{})
    total   = g.get("total_devices",0)
    offline = g.get("total_offline_devices",0)
    crits   = g.get("total_critical_alerts",0)
    tkts    = g.get("total_open_tickets",0)
    online_pct = round(((total-offline)/total*100) if total>0 else 100,1)
    risk = min(100, offline*18 + crits*9 + tkts*3)
    risk_color = "fill-red" if risk>65 else ("fill-orange" if risk>35 else "fill-green")
    risk_vc    = "val-red"  if risk>65 else ("val-orange"  if risk>35 else "val-green")
    return f"""<div class="card card-sm">
      <div class="card-head"><div class="card-icon icon-blue">📊</div><span class="card-title">System Snapshot</span></div>
      <div class="stat-row">
        <span class="stat-label">Devices Online</span>
        <span class="stat-val val-green">{online_pct}%</span>
      </div>
      {_pct_bar(online_pct,"fill-green")}
      <div class="stat-row" style="margin-top:10px">
        <span class="stat-label">Critical Alerts</span>
        <span class="stat-val val-red">{crits}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Open Tickets</span>
        <span class="stat-val val-white">{tkts}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Risk Score</span>
        <span class="stat-val {risk_vc}">{risk} / 100</span>
      </div>
      {_pct_bar(risk, risk_color)}
    </div>"""

def render_alert_reduction(metrics):
    g = metrics.get("global_metrics",{})
    crits = g.get("total_critical_alerts",0)
    total_raw = crits * 14 + 12
    filtered  = crits + 3
    noise_pct = round((1 - filtered/total_raw)*100) if total_raw > 0 else 0
    return f"""<div class="card card-sm">
      <div class="card-head"><div class="card-icon icon-teal">🔔</div><span class="card-title">Alert Reduction</span></div>
      <div class="stat-row">
        <span class="stat-label">Total Raw Alerts</span>
        <span class="stat-val val-white">{total_raw}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Filtered Relevant</span>
        <span class="stat-val val-orange">{filtered}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Noise Reduced</span>
        <span class="stat-val val-green">{noise_pct}%</span>
      </div>
      {_pct_bar(noise_pct,"fill-blue")}
    </div>"""

def render_recs(recommendations):
    rows = ""
    for rec in recommendations:
        issue = rec["issue_type"].replace("_"," ").title()
        action = rec["action"][:80]
        rows += f'<div class="bul-item"><div class="bul-dot dot-blue"></div><div><span class="bul-em">{issue}:</span> {action}</div></div>'
    if not rows:
        rows = '<div class="bul-item"><div class="bul-dot dot-green"></div>No immediate actions required.</div>'
    return f"""<div class="card card-sm">
      <div class="card-head"><div class="card-icon icon-blue">💡</div><span class="card-title">Recommended Actions</span></div>
      {rows}</div>"""

# ── section emoji map for the briefing parser ────────────────────────────────
_SECTION_MAP = {
    "top priorit":  ("🔥", "#f87171"),
    "needs immed":  ("⚠️", "#fb923c"),
    "trending":     ("📈", "#facc15"),
    "predict":      ("🔮", "#a78bfa"),
    "recommend":    ("💡", "#60a5fa"),
    "all clear":    ("✅", "#4ade80"),
}

def _parse_briefing_sections(text):
    """Split briefing text on section headers (lines starting with emoji or number)."""
    import re
    lines = text.strip().split("\n")
    sections = []
    cur_title, cur_icon, cur_color, cur_lines = None, "🤖", "#a5b4fc", []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cur_lines.append("")
            continue
        is_header = bool(re.match(r'^[0-9*\-#]*\s*[\U0001F300-\U0001FFFF\u2600-\u27BF]', stripped))
        if not is_header:
            # also treat lines ending with uppercase words after an emoji as headers
            is_header = stripped.isupper() and len(stripped) < 60
        if is_header:
            if cur_title is not None or cur_lines:
                sections.append((cur_title, cur_icon, cur_color, "\n".join(cur_lines).strip()))
            cur_title = stripped
            cur_icon, cur_color = "🤖", "#a5b4fc"
            for key, (ico, col) in _SECTION_MAP.items():
                if key in stripped.lower():
                    cur_icon, cur_color = ico, col
                    break
            cur_lines = []
        else:
            cur_lines.append(stripped)
    if cur_title is not None or cur_lines:
        sections.append((cur_title, cur_icon, cur_color, "\n".join(cur_lines).strip()))
    return sections

def _md_to_html(text, accent="#94a3b8"):
    """Convert a line of Gemini markdown to clean HTML."""
    import re
    # Escape HTML special chars first (except we already build HTML so skip < >)
    # Convert **bold**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#e2e8f0">\1</strong>', text)
    # Convert *italic* (single star, not already consumed)
    text = re.sub(r'\*(.+?)\*', r'<em style="color:#cbd5e1">\1</em>', text)
    # Convert __bold__
    text = re.sub(r'__(.+?)__', r'<strong style="color:#e2e8f0">\1</strong>', text)
    # Convert _italic_
    text = re.sub(r'_(.+?)_', r'<em style="color:#cbd5e1">\1</em>', text)
    # Strip any remaining lone * or # that weren't part of a pattern
    text = re.sub(r'(?<!\*)\*(?!\*)', '', text)
    text = re.sub(r'^#{1,6}\s*', '', text)
    return text

def render_briefing_full(text):
    """Full-width AI briefing with section parsing, markdown rendering, and scrollable pane."""
    import re
    sections = _parse_briefing_sections(text)
    inner = ""
    for i, (title, icon, color, body) in enumerate(sections):
        if title:
            # Clean markdown from the title too
            clean_title = re.sub(r'[*#_`]', '', title).strip()
            divider = f'<div style="border-top:1px solid rgba(255,255,255,0.06);margin:16px 0 14px"></div>' if i > 0 else ""
            inner += f"""{divider}
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
              <span style="font-size:1.1rem">{icon}</span>
              <span style="font-size:.92rem;font-weight:700;color:{color};letter-spacing:-.01em;text-transform:uppercase;letter-spacing:.05em">{clean_title}</span>
            </div>"""
        if body:
            body_html = ""
            for ln in body.split("\n"):
                ln = ln.strip()
                if not ln:
                    body_html += '<div style="height:8px"></div>'
                elif ln.startswith("---") or ln.startswith("***"):
                    body_html += f'<div style="border-top:1px solid rgba(255,255,255,0.06);margin:8px 0"></div>'
                elif ln.startswith(("- ", "* ", "• ")):
                    content = _md_to_html(re.sub(r'^[-*•]\s*', '', ln))
                    body_html += f'<div style="display:flex;gap:10px;padding:5px 0;line-height:1.65;font-size:.84rem"><span style="color:{color};flex-shrink:0;font-weight:700;margin-top:1px">›</span><span style="color:#94a3b8">{content}</span></div>'
                elif re.match(r'^\d+\.\s', ln):
                    num_match = re.match(r'^(\d+)\.\s+(.*)', ln)
                    if num_match:
                        num, content = num_match.group(1), _md_to_html(num_match.group(2))
                        body_html += f'<div style="display:flex;gap:10px;padding:5px 0;line-height:1.65;font-size:.84rem"><span style="color:{color};flex-shrink:0;font-weight:700;min-width:18px">{num}.</span><span style="color:#94a3b8">{content}</span></div>'
                else:
                    content = _md_to_html(ln)
                    body_html += f'<p style="color:#94a3b8;font-size:.84rem;line-height:1.8;margin:4px 0">{content}</p>'
            inner += body_html
    return f"""
    <div style="
        background:linear-gradient(145deg,#10172a 0%,#0d1420 100%);
        border:1px solid rgba(139,92,246,0.3);
        border-radius:14px;
        box-shadow:0 6px 32px rgba(139,92,246,0.1),0 2px 12px rgba(0,0,0,0.35);
        overflow:hidden;
    ">
      <div style="
          display:flex;align-items:center;justify-content:space-between;
          padding:16px 24px 14px;
          border-bottom:1px solid rgba(255,255,255,0.06);
          background:rgba(139,92,246,0.06);
      ">
        <div style="display:flex;align-items:center;gap:10px">
          <div style="width:32px;height:32px;border-radius:8px;background:rgba(139,92,246,0.2);display:flex;align-items:center;justify-content:center;font-size:16px">🤖</div>
          <span style="font-size:1rem;font-weight:700;color:#e2e8f0;letter-spacing:-.02em">AI Daily Briefing</span>
          <span style="background:rgba(139,92,246,0.15);border:1px solid rgba(139,92,246,0.3);color:#a78bfa;padding:2px 10px;border-radius:20px;font-size:.72rem;font-weight:600">{role}</span>
        </div>
        <span style="color:#475569;font-size:.75rem">Gemini AI</span>
      </div>
      <div style="
          max-height:400px;
          overflow-y:auto;
          padding:20px 24px;
          scrollbar-width:thin;
          scrollbar-color:#1e3a5f #0a1220;
      ">{inner}</div>
    </div>"""


# ─── Main ─────────────────────────────────────────────────────────────────────
if gen_btn:
    with st.spinner("Running AI Operations Pipeline…"):
        result = generate_daily_briefing(role=role)

    if result["status"] == "success":
        issues  = result["issues"]
        top     = result["top_priorities"]
        preds   = result["predictions"]
        recs    = result["recommendations"]
        briefing = result["briefing"]

        # pull metrics once
        from ingestion          import load_all_data
        from preprocessing      import preprocess_data
        from feature_extraction import extract_features
        metrics = extract_features(preprocess_data(load_all_data()))

        # ── outer padding wrapper ────────────────────────────────────────────
        st.markdown('<div style="padding:20px 28px 0;display:flex;flex-direction:column;gap:0">', unsafe_allow_html=True)

        # ── Main 8 / 4 grid ─────────────────────────────────────────────────
        left, right = st.columns([8, 4], gap="medium")

        with left:
            st.markdown(render_priorities(top),   unsafe_allow_html=True)
            st.markdown(render_attention(issues), unsafe_allow_html=True)

            # Row: Trending | Predictions
            tr_col, pr_col = st.columns(2, gap="medium")
            with tr_col:
                st.markdown(render_trending(issues),   unsafe_allow_html=True)
            with pr_col:
                st.markdown(render_predictions(preds), unsafe_allow_html=True)

            # Row: Changes | Tickets
            ch_col, tk_col = st.columns(2, gap="medium")
            with ch_col:
                st.markdown(render_changes(metrics), unsafe_allow_html=True)
            with tk_col:
                st.markdown(render_tickets(issues),  unsafe_allow_html=True)

            st.markdown(render_all_clear(issues), unsafe_allow_html=True)

        with right:
            st.markdown(render_snapshot(metrics),         unsafe_allow_html=True)
            st.markdown(render_alert_reduction(metrics),  unsafe_allow_html=True)
            st.markdown(render_recs(recs),                unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Full-width AI Briefing ──────────────────────────────────────────
        st.markdown('<div style="padding:0 28px 8px">', unsafe_allow_html=True)
        with st.expander("🤖  AI Daily Briefing  —  click to expand / collapse", expanded=True):
            st.markdown(render_briefing_full(briefing), unsafe_allow_html=True)
        with st.expander("🔍 Raw Issues Data"):
            st.json(issues)
        st.markdown('</div>', unsafe_allow_html=True)


    else:
        st.markdown(f"""<div class="card" style="border-color:rgba(239,68,68,0.4)">
          <div class="card-head"><div class="card-icon icon-red">❌</div>
          <span class="card-title" style="color:#f87171">Pipeline Failed</span></div>
          <div style="color:#64748b;font-size:.85rem">{result['message']}</div>
        </div>""", unsafe_allow_html=True)

else:
    # ── Welcome State ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="welcome">
      <div class="welcome-glow">📡</div>
      <h2>Telecom AI Operations Center</h2>
      <p>Select your role above and click <strong>Generate Briefing</strong> to run the full 7-layer AI pipeline and get your personalized operations report.</p>
      <div class="feat-grid">
        <div class="feat-card"><div class="feat-icon">🔍</div><div class="feat-label">7-Layer Pipeline</div></div>
        <div class="feat-card"><div class="feat-icon">⚡</div><div class="feat-label">Real-Time AI</div></div>
        <div class="feat-card"><div class="feat-icon">📊</div><div class="feat-label">Role-Based Reports</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="noc-footer">
  <span class="footer-text">Telecom Operations AI Backend · Powered by Gemini AI</span>
  <span class="footer-text">© 2026 NOC Platform</span>
</div>
""", unsafe_allow_html=True)
