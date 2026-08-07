import streamlit as st
from utils import CUSTOM_CSS, execute_ssh, send_active_response_alert, TELEGRAM_ENABLED

st.set_page_config(page_title="Active Response", page_icon="⚡", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("⚡ Active Response - Auto-Blocking")

def get_blocked_ips():
    command = "sudo iptables -L -n | grep DROP | awk '{print $4}' | grep -v '0.0.0.0' | sort -u"
    output, _ = execute_ssh(command, timeout=10, target="wazuh-server")
    return [ip.strip() for ip in output.split('\n') if ip.strip()] if output else []

def unblock_ip(ip):
    command = f"sudo iptables -D INPUT -s {ip} -j DROP 2>/dev/null || echo 'not blocked'"
    output, _ = execute_ssh(command, timeout=10, target="wazuh-server")
    return output

ar_col1, ar_col2 = st.columns([1, 2])

with ar_col1:
    st.markdown("### 📊 Statistics")
    stats_cmd = 'echo "Total: $(sudo grep -c \'add\' /var/ossec/active-response/active-responses.log 2>/dev/null || echo 0)" && echo "Blocked: $(sudo iptables -L -n | grep -c DROP)"'
    output, _ = execute_ssh(stats_cmd, timeout=10, target="wazuh-server")
    if output:
        stats = {}
        for line in output.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                stats[k.strip()] = v.strip()
        st.metric("Total Blocks", stats.get('Total', '0'))
        st.metric("Currently Blocked", stats.get('Blocked', '0'))

with ar_col2:
    st.markdown("### 🚫 Blocked IPs")
    blocked_ips = get_blocked_ips()
    if blocked_ips:
        st.warning(f"⚠️ {len(blocked_ips)} IPs blocked")
        for ip in blocked_ips:
            col1, col2 = st.columns([3, 1])
            with col1: st.markdown(f"🌐 **{ip}**")
            with col2:
                if st.button("🔓 Unblock", key=f"unblock_{ip}"):
                    unblock_ip(ip)
                    if TELEGRAM_ENABLED: send_active_response_alert("Unblock", ip, "Manually unblocked")
                    st.success(f"✅ {ip} unblocked!")
                    st.rerun()
    else:
        st.success("✅ No IPs blocked")
    
    st.markdown("### 🔧 Manual Block")
    manual_ip = st.text_input("IP to block", placeholder="192.168.1.100")
    if st.button("🚫 Block", use_container_width=True):
        if manual_ip:
            execute_ssh(f"sudo iptables -A INPUT -s {manual_ip} -j DROP", timeout=10, target="wazuh-server")
            if TELEGRAM_ENABLED: send_active_response_alert("Manual Block", manual_ip, "Manually blocked")
            st.success(f"✅ {manual_ip} blocked!")
            st.rerun()

st.markdown("### 📋 Active Response Rules")
rules_info = {"Rule 5710": {"description": "SSH Authentication Failure", "trigger": "Failed SSH login attempt", "action": "Block IP for 10 minutes", "risk": "HIGH"}}
for rule_id, info in rules_info.items():
    with st.expander(f"🔧 {rule_id} - {info['description']}"):
        st.markdown(f"**Trigger:** {info['trigger']}  \n**Action:** {info['action']}  \n**Risk:** <span class='risk-{info['risk'].lower()}'>{info['risk']}</span>", unsafe_allow_html=True)