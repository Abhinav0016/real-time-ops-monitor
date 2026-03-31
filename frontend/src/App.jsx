import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import {
  AlertTriangle,
  Activity,
  MapPin,
  ChevronDown,
  ChevronUp,
  MessageSquare,
  User
} from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import './index.css';
import OperationalChat from './components/Chatbot';

// Fix leafet icon bounding issues in Vite
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const ActionToggle = ({ text, colorClass = 'blue' }) => {
  const [show, setShow] = useState(false);
  return (
    <div className="action-container">
      {!show ? (
        <button className={`action-button ${colorClass}`} onClick={() => setShow(true)}>
          View Action
        </button>
      ) : (
        <div className={`action-revealed ${colorClass}`}>
          <span className="sop-badge">SOP GUIDELINE</span> {text}
          <button className="collapse-btn" onClick={() => setShow(false)}>Hide</button>
        </div>
      )}
    </div>
  );
};

const AnalystTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ backgroundColor: '#0f172a', padding: '12px', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '0.9rem', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}>
        <p style={{ margin: '0 0 8px 0', borderBottom: '1px solid #334155', paddingBottom: '4px', fontWeight: 'bold' }}>{label}</p>
        {payload.map((entry, index) => {
          let status = ''; let change = '';
          if (entry.dataKey === 'Site N') { status = 'Critical'; change = 'Near Capacity'; }
          if (entry.dataKey === 'Site H') { status = 'Growing'; change = 'Demand Surge'; }
          if (entry.dataKey === 'Site E') { status = 'Underutilized'; change = 'Low Traffic'; }

          return (
            <div key={index} style={{ marginBottom: '8px', color: entry.color }}>
              <div style={{ fontWeight: 'bold', fontSize: '1rem' }}>{entry.dataKey}: {entry.value} Units</div>
              <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '2px' }}>{status} • {change}</div>
            </div>
          );
        })}
      </div>
    );
  }
  return null;
};

const CustomDot = (props) => {
  const { cx, cy, value, stroke, dataKey } = props;
  if ((dataKey === 'Site N' && value > 60) || (dataKey === 'Site H' && value > 45)) {
    return (
      <g>
        <circle cx={cx} cy={cy} r={7} fill="#ef4444" stroke="#fff" strokeWidth={2} />
        <text x={cx} y={cy - 12} fill="#ef4444" fontSize="14" textAnchor="middle">⚠️</text>
      </g>
    );
  }
  return <circle cx={cx} cy={cy} r={5} fill={stroke} stroke="#0f172a" strokeWidth={2} />;
};


const StatusBar = ({ stats }) => {
  if (!stats) return null;
  const onlinePct = ((stats.online_devices / stats.total_devices) * 100).toFixed(1);

  return (
    <div className="status-bar fade-in">
      <div className="status-item">
        <Activity size={18} className="status-icon online" />
        <div className="status-details">
          <span className="status-label">Network Online</span>
          <span className="status-value online">{onlinePct}%</span>
        </div>
      </div>
      <div className="status-item">
        <AlertTriangle size={18} className="status-icon critical" />
        <div className="status-details">
          <span className="status-label">Critical Alerts</span>
          <span className="status-value critical">{stats.critical_alerts_count}</span>
        </div>
      </div>
      <div className="status-item">
        <MessageSquare size={18} className="status-icon alerts" />
        <div className="status-details">
          <span className="status-label">Open Tickets</span>
          <span className="status-value alerts">{stats.open_tickets_count}</span>
        </div>
      </div>
    </div>
  );
};

const InlineLabel = (props) => {
  const { x, y, stroke, value, index, dataKey, dataset } = props;
  if (!dataset || index !== dataset.length - 1) return null;
  let text = "";
  if (dataKey === "Site N") text = "Site N (Critical)";
  if (dataKey === "Site H") text = "Site H (Growing)";
  if (dataKey === "Site E") text = "Site E (Low Usage)";
  return <text x={x + 12} y={y + 4} fill={stroke} fontSize={13} fontWeight="bold">{text}</text>;
};

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userRole, setUserRole] = useState('Fleet Operations Manager');
  const [showMarketAnalysis, setShowMarketAnalysis] = useState(false);
  const [activeAnalysis, setActiveAnalysis] = useState(null);
  const [email, setEmail] = useState('');
  const [subscribeStatus, setSubscribeStatus] = useState(null);

  const handleSubscribe = async (e) => {
    e.preventDefault();
    if (!email) return;
    try {
      const response = await fetch('http://localhost:5000/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      const result = await response.json();
      if (response.ok) {
        setSubscribeStatus('Subscribed!');
        setEmail('');
        setTimeout(() => setSubscribeStatus(null), 3000);
      } else {
        setSubscribeStatus('Error: ' + result.error);
      }
    } catch (err) {
      setSubscribeStatus('Error subscribing');
    }
  };

  useEffect(() => {
    setLoading(true);
    fetch(`http://localhost:5000/api/briefing?role=${encodeURIComponent(userRole)}`)
      .then(res => res.json())
      .then(result => {
        if (result.error) throw new Error(result.error);
        setData(result);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [userRole]);

  if (loading) return <div className="loading-screen"><div className="spinner"></div><p>Initializing Operational Intelligence...</p></div>;
  const sites = data?.results?.site_locations || {};
  const siteHealth = data?.results?.site_health || {};
  const briefingText = data?.briefing || '';

  // Helper to parse briefing text into structured sections
  const getBriefingSections = (text) => {
    if (!text) return [];
    const body = text.split('OUTPUT 2: DAILY BRIEFING')[1] || text;
    const lines = body.split('\n');
    const sections = [];
    let currentSection = null;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      // Detection of headers: starts with emoji OR is a known header keyword with colon
      const isHeader = /🚨|📈|⚠️|✅|💰|💡|🔥|🧠|🔁|🔋|📅/.test(line) ||
        /^(Summary|Needs Immediate Attention|Top Priorities|Recommended Actions|Trending Issues|Active Alerts|Hardware Status|Usage Trends|Business Insights|Other Issues):/i.test(line);

      if (isHeader) {
        if (!line.includes('DAILY OPERATIONS BRIEFING')) {
          if (currentSection) sections.push(currentSection);
          let colorClass = 'blue';
          if (/🚨|🔥|Immediate|Attention/i.test(line)) colorClass = 'red';
          else if (/📈|⚠️|🧠|🔁|📅|Trending|Alerts|Usage/i.test(line)) colorClass = 'orange';
          else if (/💰|✅|🔋|Summary/i.test(line)) colorClass = 'green';
          else if (/💡|Actions/i.test(line)) colorClass = 'blue';

          currentSection = { header: line, colorClass, items: [] };
        }
      } else if (currentSection) {
        if (line.startsWith('Action:')) {
          currentSection.items.push({ type: 'action', text: line.substring(7).trim() });
        } else if (line.startsWith('↳')) {
          currentSection.items.push({ type: 'history', text: line });
        } else {
          // Catch-all: treat as an item even if it doesn't start with - or *
          const text = (line.startsWith('-') || line.startsWith('*')) ? line.substring(1).trim() : line;
          currentSection.items.push({ type: 'item', text });
        }
      }
    }
    if (currentSection) sections.push(currentSection);
    return sections;
  };

  const BriefingCard = ({ section, className = "" }) => (
    <div className={`briefing-card ${section.colorClass} ${className}`}>
      <h3 className="briefing-card-header">{section.header}</h3>
      <div className="briefing-card-content">
        {section.items.map((item, i) => {
          if (item.type === 'action') return <ActionToggle key={i} text={item.text} colorClass={section.colorClass} />;
          if (item.type === 'item') return <div key={i} className="briefing-item">- {item.text}</div>;
          if (item.type === 'history') return <div key={i} className="briefing-history">{item.text}</div>;
          return null;
        })}
      </div>
    </div>
  );

  const sections = getBriefingSections(briefingText);
  // Improved detection of priorities
  const prioritySection = sections.find(s => /Needs Immediate Attention|Top Priorities/i.test(s.header));
  const otherSections = sections.filter(s => !/Needs Immediate Attention|Top Priorities|Summary|Recommended Actions/i.test(s.header));
  const summarySection = sections.find(s => /Summary/i.test(s.header));
  const recommendationSection = sections.find(s => /Recommended Actions/i.test(s.header));

  console.log("Briefing Sections:", { prioritySection, otherSections, summarySection, recommendationSection });

  const formattedTrendData = data?.results?.charts?.trend_data?.map((d, i) => ({
    ...d,
    day_label: `Day ${i + 1}`
  })) || [];

  if (error) return <div className="error-screen"><AlertTriangle size={48} color="var(--accent-red)" /><p>{error}</p></div>;

  return (
    <div className="dashboard">
      <header className="glass-header">
        <div className="header-main">
          <Activity className="header-icon" />
          <h1>Telecom Network Operations Briefing</h1>
        </div>

        <div className="role-selector-container">
          <label>Operational View:</label>
          <User className="role-icon" size={16} />
          <select value={userRole} onChange={(e) => setUserRole(e.target.value)} className="role-dropdown">
            <option value="Fleet Operations Manager">Fleet Operations Manager</option>
            <option value="NOC Analyst">NOC Analyst</option>
            <option value="Site Supervisor">Site Supervisor</option>
          </select>
        </div>

        <div className="subscription-container">
          <form onSubmit={handleSubscribe} className="subscribe-form">
            <input
              type="email"
              placeholder="Email for Alerts"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="subscribe-input"
              required
            />
            <button type="submit" className="subscribe-btn">Subscribe</button>
          </form>
          {subscribeStatus && <span className="subscribe-status">{subscribeStatus}</span>}
        </div>

        <div className="status-badge pulse-green">SYSTEMS ONLINE</div>

      </header>
      <StatusBar stats={data?.results?.stats} />

      <main className="dashboard-content">
        {/* Row 1: Priorities & Map */}
        <div className="dashboard-top-row">
          <div className="briefing-panel glass-panel priority-panel">
            <div className="panel-header">
              <AlertTriangle className="section-icon" />
              <h2>Critical Operations</h2>
            </div>
            <div className="priority-content">
              {prioritySection ? <BriefingCard section={prioritySection} className="full-height" /> : <p className="no-data">No critical issues detected.</p>}
            </div>
          </div>

          <section className="map-panel glass-panel">
            <div className="panel-header">
              <MapPin className="section-icon" />
              <h2>Live Network Visualization</h2>
            </div>
            <div className="map-wrapper">
              <MapContainer center={[22.0, 78.96]} zoom={4.5} scrollWheelZoom={false} className="leaflet-map">
                <TileLayer
                  attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />
                {Object.keys(sites).map(siteKey => {
                  const site = sites[siteKey];
                  const health = siteHealth[siteKey] || { color: 'green', reason: 'Normal' };
                  let markerColor = health.color === 'red' ? "var(--accent-red)" : (health.color === 'orange' ? "var(--accent-orange)" : "var(--accent-green)");
                  let status = health.color === 'red' ? "Critical Alert" : (health.color === 'orange' ? "Warning" : "Normal");
                  let pulseClass = health.color === 'red' ? "pulse-marker-red" : "";

                  const customIcon = L.divIcon({
                    className: 'custom-pin',
                    html: `<div class="map-marker ${pulseClass}" style="background-color: ${markerColor};"></div>`,
                    iconSize: [24, 24],
                    iconAnchor: [12, 12]
                  });

                  return (
                    <Marker position={[site.lat, site.lon]} icon={customIcon} key={siteKey}>
                      <Popup className="glass-popup">
                        <strong>Site {siteKey}</strong><br />
                        Status: <span style={{ color: markerColor, fontWeight: 'bold' }}>{status}</span><br />
                        Reason: <span style={{ color: '#ddd' }}>{health.reason}</span>
                      </Popup>
                    </Marker>
                  )
                })}
              </MapContainer>
            </div>
          </section>
        </div>

        {/* Row 2: Trends & Others */}
        <div className="dashboard-mid-row">
          {otherSections.map((s, i) => (
            <BriefingCard key={i} section={s} />
          ))}
        </div>

        {/* Row 3: Summary & Recommendations */}
        <div className="dashboard-bottom-row">
          {summarySection && <BriefingCard section={summarySection} className="full-width" />}
          {recommendationSection && <BriefingCard section={recommendationSection} className="full-width" />}
        </div>
      </main>

      {/* Market Analysis Section */}
      <section className="market-analysis-section">
        {!showMarketAnalysis ? (
          <button className="market-analysis-btn" onClick={() => setShowMarketAnalysis(true)}>
            Market Analysis
          </button>
        ) : (
          <div className="modal-overlay" onClick={() => { setShowMarketAnalysis(false); setActiveAnalysis(null); }}>
            <div className="modal-content glass-panel" onClick={(e) => e.stopPropagation()}>
              <button className="close-modal" onClick={() => { setShowMarketAnalysis(false); setActiveAnalysis(null); }}>×</button>

              <div className="analysis-options-container">
                <div className="options-header">
                  <h3>Market Analysis Explorer</h3>
                </div>
                <div className="analysis-options">
                  <button
                    className={`option-btn ${activeAnalysis === 'usage' ? 'active' : ''}`}
                    onClick={() => setActiveAnalysis('usage')}
                  >
                    1. Usage Trends
                  </button>
                  <button
                    className={`option-btn ${activeAnalysis === 'comparison' ? 'active' : ''}`}
                    onClick={() => setActiveAnalysis('comparison')}
                  >
                    2. Site Comparison
                  </button>
                  <button
                    className={`option-btn ${activeAnalysis === 'business' ? 'active' : ''}`}
                    onClick={() => setActiveAnalysis('business')}
                  >
                    3. Business Analysis
                  </button>
                </div>
              </div>

              {/* Analytics Charts Section (Inside Modal) */}
              {data?.results?.charts && activeAnalysis && (
                <div className="modal-charts-container single-chart">
                  {activeAnalysis === 'usage' && (
                    <div className="chart-panel fade-in">
                      <h3>📈 Usage Trends</h3>
                      <div style={{ height: 300 }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={formattedTrendData} margin={{ top: 20, right: 140, left: 10, bottom: 25 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                            <XAxis dataKey="day_label" stroke="#aaa" tick={{ fill: '#e2e8f0' }} axisLine={false} tickLine={false} />
                            <YAxis stroke="#aaa" label={{ value: 'Data Usage (Units)', angle: -90, position: 'insideLeft', offset: 0, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                            <Tooltip content={<AnalystTooltip />} cursor={{ stroke: '#334155', strokeWidth: 2 }} />

                            <ReferenceLine y={60} stroke="#ef4444" strokeDasharray="4 4" strokeOpacity={0.8} label={{ value: 'Critical Capacity Threshold', position: 'insideBottomRight', fill: '#ef4444', fontSize: 11 }} />

                            <Line type="monotone" dataKey="Site N" stroke="#ef4444" strokeWidth={4} dot={(props) => <CustomDot {...props} dataKey="Site N" />} activeDot={{ r: 8 }} isAnimationActive={false}>
                              <InlineLabel dataset={formattedTrendData} dataKey="Site N" stroke="#ef4444" />
                            </Line>

                            <Line type="monotone" dataKey="Site H" stroke="#f97316" strokeWidth={4} dot={(props) => <CustomDot {...props} dataKey="Site H" />} activeDot={{ r: 8 }} isAnimationActive={false}>
                              <InlineLabel dataset={formattedTrendData} dataKey="Site H" stroke="#f97316" />
                            </Line>

                            <Line type="monotone" dataKey="Site E" stroke="#22c55e" strokeWidth={4} dot={(props) => <CustomDot {...props} dataKey="Site E" />} activeDot={{ r: 8 }} isAnimationActive={false}>
                              <InlineLabel dataset={formattedTrendData} dataKey="Site E" stroke="#22c55e" />
                            </Line>
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                      <div style={{ textAlign: 'center', marginTop: '1rem', color: '#e2e8f0', fontSize: '0.95rem', padding: '0.6rem', background: 'rgba(255,255,255,0.05)', borderRadius: '6px', fontWeight: '500' }}>
                        Site N is near capacity ⚠️ , Site H demand is increasing 📈 , Site E is underutilized 📉
                      </div>
                    </div>
                  )}

                  {activeAnalysis === 'comparison' && (
                    <div className="chart-panel fade-in">
                      <h3>📊 Site Comparison: Current Load</h3>
                      <div style={{ height: 300 }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={data.results.charts.site_stats.slice(0, 8)} margin={{ top: 20, right: 30, left: 10, bottom: 25 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis dataKey="site" stroke="#aaa" label={{ value: 'Network Site', position: 'insideBottom', offset: -15, fill: '#94a3b8' }} />
                            <YAxis stroke="#aaa" label={{ value: 'Data Usage (GB)', angle: -90, position: 'insideLeft', offset: 0, fill: '#94a3b8' }} />
                            <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#fff' }} cursor={{ fill: '#222' }} />
                            <Bar dataKey="usage" fill="#3b82f6" name="Usage (GB) / 24hrs" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  )}

                  {activeAnalysis === 'business' && (
                    <div className="chart-panel fade-in">
                      <h3>💰 Business Analysis: Cost vs Profit</h3>
                      <div style={{ height: 300 }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={data.results.charts.site_stats.slice(0, 8)} margin={{ top: 30, right: 30, left: 10, bottom: 25 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis dataKey="site" stroke="#aaa" label={{ value: 'Network Site', position: 'insideBottom', offset: -15, fill: '#94a3b8' }} />
                            <YAxis stroke="#aaa" label={{ value: 'Net Value (Units)', angle: -90, position: 'insideLeft', offset: 0, fill: '#94a3b8' }} />
                            <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#fff' }} cursor={{ fill: '#222' }} />
                            <Legend wrapperStyle={{ paddingTop: '20px' }} />
                            <Bar dataKey="cost" stackId="a" fill="#ef4444" name="Est. Cost" />
                            <Bar dataKey="profit" stackId="a" fill="#22c55e" name="Net Profit" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </section>

      <OperationalChat userRole={userRole} />
    </div>
  );
}

export default App;
