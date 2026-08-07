import streamlit as st
from utils import CUSTOM_CSS, get_wazuh_token, get_agents, ATTACKS_DB, TELEGRAM_ENABLED, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, send_telegram_message

# ============ إعدادات الصفحة ============
st.set_page_config(page_title="R&M PurpleOps Pro - Home", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============ Sidebar ============
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <div style='font-size: 3rem;'>🛡️</div>
        <h2 style='margin: 0; color: #f1f5f9;'>PurpleOps Pro</h2>
        <p style='color: #94a3b8; margin: 5px 0;'>Security Assessment Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🔌 System Status")
    try:
        token = get_wazuh_token()
        st.markdown('<span class="status-badge status-success">✓ Wazuh API Connected</span>', unsafe_allow_html=True)
    except:
        st.markdown('<span class="status-badge status-danger">✗ Wazuh API Disconnected</span>', unsafe_allow_html=True)
    
    try:
        agents = get_agents(token)
        active = len([a for a in agents if a['status'] == 'active'])
        total = len(agents)
        st.markdown(f"**Agents:** {active}/{total} Active")
    except:
        st.warning("Unable to fetch agents")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📱 Telegram Alerts")
    if TELEGRAM_ENABLED and TELEGRAM_BOT_TOKEN:
        st.markdown('<span class="status-badge status-success">✓ Connected</span>', unsafe_allow_html=True)
        if st.button("🔔 Test Notification", use_container_width=True):
            success, msg = send_telegram_message("🛡️ <b>Test Message</b>\n✅ Telegram is working!")
            if success: st.success("✅ Sent!")
            else: st.error(f"❌ {msg}")
    else:
        st.markdown('<span class="status-badge status-danger">✗ Disabled</span>', unsafe_allow_html=True)

# ============ Main Header ============
st.title("🛡️ R&M PurpleOps Pro")
st.markdown("""
<div style='background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 15px; border-radius: 4px; margin: 20px 0;'>
    <strong>🎯 Mission:</strong> Automate Purple Team exercises to validate SOC detection capabilities against real-world threats
</div>
""", unsafe_allow_html=True)

# ============ Hero Metrics ============
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='metric-card'><div style='color: #94a3b8; font-size: 0.85rem;'>TOTAL TECHNIQUES</div><div style='font-size: 2.5rem; font-weight: 800; color: #3b82f6;'>{len(ATTACKS_DB)}</div><div style='color: #64748b; font-size: 0.85rem;'>MITRE ATT&CK</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div style='color: #94a3b8; font-size: 0.85rem;'>TACTICS COVERED</div><div style='font-size: 2.5rem; font-weight: 800; color: #8b5cf6;'>{len(set(a['tactic'] for a in ATTACKS_DB.values()))}</div><div style='color: #64748b; font-size: 0.85rem;'>Attack Categories</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='metric-card'><div style='color: #94a3b8; font-size: 0.85rem;'>PLATFORM STATUS</div><div style='font-size: 2.5rem; font-weight: 800; color: #22c55e;'>●</div><div style='color: #64748b; font-size: 0.85rem;'>Active & Monitoring</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown("<div class='metric-card'><div style='color: #94a3b8; font-size: 0.85rem;'>DETECTION RATE</div><div style='font-size: 2.5rem; font-weight: 800; color: #22c55e;'>90%</div><div style='color: #64748b; font-size: 0.85rem;'>9/10 Detected</div></div>", unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============ Platform Features ============
st.markdown("## 🚀 Platform Features")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class='metric-card'>
        <h3 style='margin-top: 0;'>🎯 Attack Simulation</h3>
        <p style='color: #94a3b8;'>Execute MITRE ATT&CK techniques and validate SOC detection capabilities in real-time.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class='metric-card'>
        <h3 style='margin-top: 0;'>🦖 EDR Live Response</h3>
        <p style='color: #94a3b8;'>Perform live forensics on connected endpoints (Linux & Windows) via Velociraptor.</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class='metric-card'>
        <h3 style='margin-top: 0;'>⚡ Active Response</h3>
        <p style='color: #94a3b8;'>Automatically block malicious IPs and respond to threats in real-time.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============ Footer ============
st.markdown("""
<div style='text-align: center; padding: 30px; color: #64748b;'>
    <p style='font-size: 1.1rem; margin: 5px 0;'>🛡️ <strong>R&M PurpleOps Pro v3.1</strong></p>
    <p style='font-size: 0.8rem; margin: 10px 0;'>Powered by Python + Wazuh + OpenSearch + Velociraptor + MITRE ATT&CK</p>
</div>
""", unsafe_allow_html=True)