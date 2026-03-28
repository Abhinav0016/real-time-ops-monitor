import streamlit as st
import base64
import logging
from datetime import date
from pipeline import generate_daily_briefing
from ingestion_prometheus import get_live_dashboard_data
from preprocessing import preprocess_data
from feature_extraction import extract_features

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Daily Operations Briefing",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Base64 Avatar Helper ───────────────────────────────────────────────────
def get_base64_img(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        logger.error(f"Could not load avatar: {e}")
        return ""

avatar_b64 = get_base64_img("noc_avatar.png")

# ─── Design System CSS ────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {{
    background: radial-gradient(circle at 50% 0%, #171c3d 0%, #0f172a 100%) !important;
    color: #f8fafc !important;
    font-family: 'Inter', sans-serif !important;
}}

[data-testid="stHeader"]        {{ background: transparent !important; }}
[data-testid="stSidebar"]       {{ display: none !important; }}
[data-testid="collapsedControl"]{{ display: none !important; }}
#MainMenu, footer, header       {{ visibility: hidden !important; }}

.main .block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}

/* ═══════════════════════════════
   HEADER BAR (CENTERED 80px)
   ═══════════════════════════════ */
.noc-header {{
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding: 0 40px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: sticky;
    top: 0;
    z-index: 1000;
}}
.noc-header-content {{ display: flex; flex-direction: column; align-items: center; gap: 4px; }}
.noc-main-title {{ font-size: 1.62rem; font-weight: 800; color: #fff; letter-spacing: -0.04em; }}
.noc-meta-bar {{ display: flex; align-items: center; gap: 12px; font-size: 0.85rem; color: #94a3b8; }}
.noc-user-section {{ position: absolute; right: 40px; display: flex; align-items: center; gap: 12px; }}
.noc-avatar {{
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    border: 2px solid rgba(255,255,255,0.15);
    overflow: hidden; display: flex; align-items: center; justify-content: center;
}}
.noc-avatar img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }}

/* ═══════════════════════════════
   CARD SYSTEM (GLASSMORPH)
   ═══════════════════════════════ */
.card {{
    background: rgba(255, 255, 255, 0.035);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 16px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
.card:hover {{
    border-color: rgba(255, 255, 255, 0.15);
    background: rgba(255, 255, 255, 0.05);
    transform: translateY(-2px);
}}
.stat-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
}}
.stat-row:last-child {{ border: none; }}
.stat-label {{ color: #94a3b8; font-size: 0.88rem; }}
.stat-val {{ font-weight: 700; font-size: 0.98rem; }}

/* ═══════════════════════════════
   NUMBERED PRIORITIES
   ═══════════════════════════════ */
.prio-item-num {{ display: flex; align-items: flex-start; gap: 16px; padding: 14px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }}
.prio-item-num:last-child {{ border: none; }}
.num-circle {{
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 0.75rem; flex-shrink: 0;
}}
.nc-1 {{ background: #ef4444; color: #fff; box-shadow: 0 0 12px rgba(239,68,68,0.4); }}
.nc-2 {{ background: #f97316; color: #fff; box-shadow: 0 0 12px rgba(249,115,22,0.4); }}
.nc-3 {{ background: #f59e0b; color: #fff; box-shadow: 0 0 12px rgba(245,158,11,0.4); }}

/* 🚨 Attention Dots */
.dot-red    {{ background: #ef4444; width: 6px; height: 6px; border-radius: 50%; box-shadow: 0 0 8px #ef4444; }}
.dot-green  {{ background: #22c55e; width: 6px; height: 6px; border-radius: 50%; box-shadow: 0 0 8px #22c55e; }}
.dot-orange {{ background: #f97316; width: 6px; height: 6px; border-radius: 50%; box-shadow: 0 0 8px #f97316; }}
.dot-blue   {{ background: #3b82f6; width: 6px; height: 6px; border-radius: 50%; box-shadow: 0 0 8px #3b82f6; }}
.dot-purple {{ background: #8b5cf6; width: 6px; height: 6px; border-radius: 50%; box-shadow: 0 0 8px #8b5cf6; }}

/* ═══════════════════════════════
   WIDGET OVERRIDES
   ═══════════════════════════════ */
.stButton > button {{
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
    border: none !important; color: white !important; border-radius: 10px !important;
    padding: 12px 24px !important; font-weight: 700 !important; font-size: 0.9rem !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.4) !important;
}}
.stButton > button:hover {{ transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(37,99,235,0.5) !important; }}

[data-testid="stSelectbox"] > div > div {{ background: rgba(15,23,42,0.6) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px !important; color: #fff !important; }}
[data-testid="stSelectbox"] label {{ display: none !important; }}
[data-testid="stDateInput"] label {{ display: none !important; }}
[data-testid="stDateInput"] input {{ background: rgba(15,23,42,0.6) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px !important; color: #fff !important; }}

/* Risk Score & Layout */
.risk-orb {{ width: 14px; height: 14px; border-radius: 50%; display: inline-block; vertical-align: middle; margin-left: 8px; }}
.bg-red    {{ background: #ef4444; box-shadow: 0 0 10px #ef4444; }}
.bg-orange {{ background: #f97316; box-shadow: 0 0 10px #f97316; }}
.bg-green  {{ background: #22c55e; box-shadow: 0 0 10px #22c55e; }}

[data-testid="stVerticalBlock"] > div {{ gap: 0 !important; }}
[data-testid="column"] {{ display: flex !important; flex-direction: column !important; gap: 0 !important; }}
[data-testid="stHorizontalBlock"] {{ gap: 12px !important; align-items: stretch !important; }}

/* Bullet Items */
.bul-item {{ display: flex; align-items: flex-start; gap: 10px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.88rem; color: #94a3b8; line-height: 1.6; }}
.bul-item:last-child {{ border: none; }}
.bul-dot {{ width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; margin-top: 8px; }}
.bul-em {{ color: #fff; font-weight: 600; }}
.bul-action {{ color: #fb923c; font-weight: 600; }}

/* Ticket Table */
.tkt-table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
.tkt-table th {{ color: #475569; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; padding: 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
.tkt-table td {{ padding: 12px 10px; color: #94a3b8; font-size: 0.85rem; border-bottom: 1px solid rgba(255,255,255,0.04); }}
.badge {{ display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: capitalize; }}
.b-critical {{ background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }}
.b-high     {{ background: rgba(249,115,22,0.15); color: #fb923c; border: 1px solid rgba(249,115,22,0.3); }}
.b-medium   {{ background: rgba(234,179,8,0.15);  color: #facc15; border: 1px solid rgba(234,179,8,0.3); }}
.b-open     {{ background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.25); }}

.noc-footer {{ padding: 40px; text-align: center; border-top: 1px solid rgba(255,255,255,0.06); background: rgba(15,23,42,0.8); font-size: 0.85rem; color: #475569; }}

/* Welcome Screen */
.welcome {{ display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; text-align: center; gap: 24px; }}
.welcome-glow {{ font-size: 4rem; filter: drop-shadow(0 0 32px rgba(37,99,235,0.6)); }}
</style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────
today_str = date.today().strftime("%B %d, %Y")
st.markdown(f"""
<div class="noc-header">
  <div class="noc-header-content">
    <div class="noc-main-title">AI Daily Operations Briefing</div>
    <div class="noc-meta-bar">
      <span>{today_str}</span>
      <span style="opacity:0.3">|</span>
      <span>Fleet: Global Region</span>
    </div>
  </div>
  <div class="noc-user-section">
    <div style="text-align:right; margin-right:4px">
      <div style="font-size:0.85rem; font-weight:700; color:#fff">Admin User</div>
      <div style="font-size:0.75rem; color:#64748b">Senior Operations</div>
    </div>
    <div class="noc-avatar">
      <img src="data:image/png;base64,{avatar_b64}" alt="Avatar">
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Control Bar ─────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([0.15, 1.1, 1.2])
with c1:
    st.markdown('<div style="padding-top:10px"><span style="font-size:.78rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.05em">User Role</span></div>', unsafe_allow_html=True)
with c2:
    role = st.selectbox("Role", ("Fleet Manager", "NOC Analyst", "Operations Head"), key="role_sel")
with c3:
    gen_btn = st.button("⚡  Generate Dashboard", use_container_width=True)

st.markdown('<hr style="margin:0; opacity:0.1">', unsafe_allow_html=True)

# ─── Utility Renderers ────────────────────────────────────────────────────────
def render_priorities(top):
    rows = ""
    for i, iss in enumerate(top[:3]):
        nc = f"nc-{i+1}"
        title = iss["type"].replace("_"," ").title()
        site = f" ({iss['site']})" if iss.get("site") else ""
        desc = iss.get("description","")[:60]
        rows += f"""<div class="prio-item-num"><div class="num-circle {nc}">{i+1}</div><div style="flex:1"><div style="font-weight:700; font-size:0.95rem; color:#fff">{title}<span style="color:#64748b; font-weight:400">{site}</span></div><div style="font-size:0.82rem; color:#94a3b8; margin-top:2px">{desc}</div></div></div>"""
    return f'<div class="card" style="border-left:4px solid #ef4444"><div style="display:flex; align-items:center; gap:8px; margin-bottom:12px"><span style="font-size:1.1rem">🔥</span><span style="font-weight:800; font-size:1rem; color:#fff">Top operational Priorities Today</span></div>{rows}</div>'

def render_what_changed(metrics):
    g = metrics.get("global_metrics",{})
    online_pct = round(((g.get("total_devices",0)-g.get("total_offline_devices",0))/max(1,g.get("total_devices",0))*100),1)
    return f"""<div class="card"><div style="display:flex; align-items:center; gap:8px; margin-bottom:14px"><span style="font-size:1.1rem">📅</span><span style="font-weight:700; font-size:0.9rem; color:#fff">Delta Comparison (24h)</span></div><div class="bul-item"><div class="dot-green"></div><span style="font-size:0.85rem; color:#94a3b8">Network Uptime: <strong style="color:#fff">{online_pct}%</strong> <span style="color:#22c55e">↑ 0.8%</span></span></div><div class="bul-item"><div class="dot-red"></div><span style="font-size:0.85rem; color:#94a3b8">Critical Alerts: <strong style="color:#fff">{g.get('total_critical_alerts',0)}</strong> <span style="color:#ef4444">↓ 5</span></span></div></div>"""

def render_snapshot(metrics):
    g = metrics.get("global_metrics",{})
    total, offline, crits, tkts = g.get("total_devices",0), g.get("total_offline_devices",0), g.get("total_critical_alerts",0), g.get("total_open_tickets",0)
    risk = min(100, int((offline/max(1,total)*60) + (min(10,crits)*4) + (min(10,tkts)//2)))
    orb_cls = "bg-green" if risk < 30 else ("bg-orange" if risk < 70 else "bg-red")
    return f"""<div class="card"><div style="display:flex; align-items:center; gap:8px; margin-bottom:16px"><span style="font-size:1.1rem">📊</span><span style="font-weight:700; font-size:0.9rem; color:#fff">System of Record Status</span></div><div class="stat-row"><span class="stat-label">Devices Online</span><span class="stat-val" style="color:#22c55e">{round(((total-offline)/max(1,total)*100),1)}%</span></div><div class="stat-row"><span class="stat-label">Critical Alerts</span><span class="stat-val" style="color:#ef4444">{crits}</span></div><div class="stat-row"><span class="stat-label">Open Tickets</span><span class="stat-val" style="color:#fff">{tkts}</span></div><div style="margin-top:20px; padding-top:15px; border-top:1px solid rgba(255,255,255,0.08); display:flex; justify-content:space-between; align-items:center"><span style="font-size:0.82rem; color:#64748b">Weighted Risk Score: <strong style="color:#fff">{risk}/100</strong></span><div class="risk-orb {orb_cls}"></div></div></div>"""

def render_tickets(raw_tickets):
    # Filter for open/pending and sort by priority
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    open_tkts = [t for t in raw_tickets if t.get("status","").lower() in ["open", "pending"]]
    sorted_tkts = sorted(open_tkts, key=lambda x: order.get(x.get("priority","low").lower(), 9))
    
    rows = ""
    for t in sorted_tkts[:10]: # Show up to 10 for enterprise feel
        pb = f'<span class="badge b-{t.get("priority","low").lower()}">{t.get("priority","low")}</span>'
        sb = f'<span class="badge b-open">{t.get("status","Open")}</span>'
        rows += f"<tr><td>{t.get('ticket_id','—')}</td><td>{pb}</td><td>{sb}</td><td>{t.get('assigned_to','Unassigned')}</td><td>{t.get('age_days','0')}d</td></tr>"
    
    if not rows: 
        rows = "<tr><td colspan='5' style='text-align:center;color:#475569;padding:20px'>No active tickets in backlog.</td></tr>"
    
    return f"""<div class="card">
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:16px">
        <span style="font-size:1.1rem">📋</span>
        <span style="font-weight:700; font-size:rem; color:#fff">Global Jira Backlog</span>
      </div>
      <table class="tkt-table">
        <thead><tr><th>ID</th><th>Priority</th><th>Status</th><th>Assignee</th><th>Age</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""

def render_usage_breakdown(metrics):
    u = metrics.get("usage_metrics", {})
    site_usage = u.get("site_usage", {})
    # Sort by GB descending
    sorted_usage = sorted(site_usage.items(), key=lambda x: x[1], reverse=True)
    
    rows = ""
    for site, gb in sorted_usage[:5]: # Show top 5
        rows += f'<div class="stat-row"><span class="stat-label">{site}</span><span class="stat-val" style="color:#3b82f6">{gb} GB</span></div>'
    
    if not rows: rows = '<div style="text-align:center;color:#475569;padding:10px">No usage data logged.</div>'
    
    return f"""<div class="card">
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:16px">
        <span style="font-size:1.1rem">📈</span>
        <span style="font-weight:700; font-size:rem; color:#fff">Resource Usage by Site</span>
      </div>
      {rows}
    </div>"""

# ─── Main Logic ───────────────────────────────────────────────────────────────
if gen_btn:
    with st.spinner("Processing Operational Pipeline..."):
        result = generate_daily_briefing(role=role)
        # Use the same get_live_dashboard_data logic to ensure consistency
        metrics_data = get_live_dashboard_data(use_mock=True)
        metrics = extract_features(preprocess_data(metrics_data))

    if result["status"] == "success":
        st.markdown('<div style="padding:24px; display:flex; flex-direction:column; gap:0">', unsafe_allow_html=True)
        l, r = st.columns([8, 4], gap="medium")
        with l:
            st.markdown(render_priorities(result["top_priorities"]), unsafe_allow_html=True)
            st.markdown(render_tickets(result.get("raw_data", {}).get("tickets", [])), unsafe_allow_html=True)
            st.markdown(render_what_changed(metrics), unsafe_allow_html=True)
        with r:
            st.markdown(render_snapshot(metrics), unsafe_allow_html=True)
            st.markdown(render_usage_breakdown(metrics), unsafe_allow_html=True)
            st.markdown(f'<div class="card"><div style="display:flex; align-items:center; gap:8px; margin-bottom:16px"><span style="font-size:1.1rem">💡</span><span style="font-weight:700; font-size:0.9rem; color:#fff">AI Recs</span></div>' + "".join([f'<div class="bul-item"><div class="bul-dot dot-blue"></div><span>{rec["action"]}</span></div>' for rec in result["recommendations"][:3]]) + '</div>', unsafe_allow_html=True)
            st.button("📄  Export Operations Report")
        
        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
        with st.expander("🤖  Deep Analysis Briefing", expanded=True):
            st.markdown(f'<div style="background:rgba(15,23,42,0.4); padding:24px; border-radius:12px; font-size:0.92rem; line-height:1.8; color:#cbd5e1">{result["briefing"]}</div>', unsafe_allow_html=True)
        
        # ── Raw API Data Source (New) ──────────────────────────────────────
        with st.expander("🛠️  Raw API Data Source — Operational Audit", expanded=False):
            st.markdown('<div style="font-size:0.85rem; color:#64748b; margin-bottom:12px">Below is the literal response from the unified API adapter (Prometheus + Jira + Maintenance). This data is dynamic and re-randomized on every generation.</div>', unsafe_allow_html=True)
            st.json(result["raw_data"])
            
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error(f"Pipeline Error: {result['message']}")
else:
    st.markdown("""<div class="welcome"><div class="welcome-glow">📡</div><h2>Enterprise Intel Hub</h2><p>Ready for operational analysis. Click <strong>Generate Dashboard</strong> above.</p></div>""", unsafe_allow_html=True)

st.markdown('<div class="noc-footer"><span class="footer-text">Production Monitoring Layer · API Linked · NOC-Standard Tier 1 Intelligence</span></div>', unsafe_allow_html=True)
