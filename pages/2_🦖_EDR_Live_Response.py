import streamlit as st
from utils import CUSTOM_CSS, VELOCIRAPTOR_CLIENTS, SSH_CONNECTIONS, execute_ssh

st.set_page_config(page_title="EDR Live Response", page_icon="🦖", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("🦖 Velociraptor EDR - Live Response")

edr_col1, edr_col2 = st.columns([1, 2])

with edr_col1:
    st.markdown("### 📡 Connected Clients")
    st.success(f"✅ {len(VELOCIRAPTOR_CLIENTS)} clients registered")
    for client in VELOCIRAPTOR_CLIENTS:
        os_icon = "🐧" if client["os"] == "linux" else "🪟"
        os_color = "#22c55e" if client["os"] == "linux" else "#3b82f6"
        st.markdown(f"""
        <div style='background: rgba(34, 197, 94, 0.1); padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 4px solid {os_color};'>
            <strong style='color: {os_color}; font-size: 1.1rem;'>{os_icon} {client["hostname"]}</strong><br>
            <small style='color: #94a3b8;'>ID: {client["client_id"]}</small><br>
            <small style='color: #64748b;'>OS: {client["os"].title()} | IP: {client["ip"]}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Quick Stats")
    stats_commands = {"Total Processes": "ps aux | wc -l", "Active Users": "who | wc -l", "Open Connections": "netstat -an | grep ESTABLISHED | wc -l", "Disk Usage": "df -h / | tail -1 | awk '{print $5}'"}
    stats_cols = st.columns(2)
    for idx, (stat_name, cmd) in enumerate(stats_commands.items()):
        output, _ = execute_ssh(cmd, timeout=5, target="wazuh-server")
        if output:
            with stats_cols[idx % 2]:
                st.metric(stat_name, output.strip())

with edr_col2:
    st.markdown("### 🔍 Live Forensics")
    client_options = {c["hostname"]: c for c in VELOCIRAPTOR_CLIENTS}
    selected_client = st.selectbox("Select Client", options=list(client_options.keys()), format_func=lambda x: f"{x} ({client_options[x]['os'].title()})")
    client_os = client_options[selected_client]["os"]
    
    forensic_options = {
        "linux": {"🖥️ System Info": "uname -a && hostname && whoami && uptime", "⚙️ Running Processes": "ps aux --sort=-%cpu | head -20", "🌐 Network Connections": "netstat -tulnp | grep ESTABLISHED", "🚪 Open Ports": "ss -tulnp", "👤 Recent Logins": "last -n 10", "🔍 Suspicious Files": "find /tmp /var/tmp -type f -mtime -1 2>/dev/null | head -20"},
        "windows": {"🖥️ System Info": "systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\"", "⚙️ Running Processes": "tasklist /FO CSV /NH", "🌐 Network Connections": "netstat -ano | findstr ESTABLISHED", "🚪 Open Ports": "netstat -ano | findstr LISTENING", "👤 Logged Users": "query user", "⏰ Scheduled Tasks": "schtasks /query /fo CSV /NH"}
    }
    
    selected_forensic = st.selectbox("Select Forensic Type", options=list(forensic_options[client_os].keys()))
    
    if st.button("🔍 Execute Forensic", use_container_width=True, type="primary"):
        with st.spinner(f"Executing {selected_forensic} on {selected_client}..."):
            command = forensic_options[client_os][selected_forensic]
            output, error = execute_ssh(command, timeout=20, target=selected_client)
            if output:
                st.success(f"✅ Completed on {selected_client}!")
                st.code(output, language='powershell' if client_os == "windows" else 'bash')
            else:
                st.error(f"❌ Error: {error}")

st.markdown("### 🎯 Advanced Forensics")
adv_col1, adv_col2 = st.columns(2)
with adv_col1:
    custom_command = st.text_area("Custom Command", placeholder="e.g., find / -name '*.sh' -mtime -1", height=100, key="custom_cmd")
    custom_target = st.selectbox("Select Target", options=list(SSH_CONNECTIONS.keys()), key="custom_target")
    if st.button("⚡ Execute", use_container_width=True):
        if custom_command:
            output, error = execute_ssh(custom_command, timeout=30, target=custom_target)
            if output:
                st.success("✅ Command executed!")
                st.code(output, language='bash')
            else:
                st.error(f"❌ Error: {error}")

with adv_col2:
    threat_checks = {"🦠 Cryptominers": "ps aux | grep -iE 'xmrig|stratum|minerd' | grep -v grep", "🔓 SSH Backdoors": "find / -name 'authorized_keys' 2>/dev/null", "🕵️ Suspicious SUID": "find / -perm -4000 -type f 2>/dev/null | head -20", "📡 Reverse Shells": "netstat -tulnp | grep -E ':(4444|5555|8888|9999)'"}
    selected_threat = st.selectbox("Threat Check", options=list(threat_checks.keys()), key="threat_check")
    if st.button("🔎 Run Check", use_container_width=True):
        output, _ = execute_ssh(threat_checks[selected_threat], timeout=20, target="wazuh-server")
        if output:
            st.warning("⚠️ Findings detected:")
            st.code(output, language='bash')
        else:
            st.success("✅ No threats detected")