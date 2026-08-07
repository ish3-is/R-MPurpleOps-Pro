import streamlit as st
import requests
import urllib3
import os
import paramiko
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# ============ إعدادات الاتصال ============
WAZUH_API_URL = "https://192.168.1.14:55000"
WAZUH_USER = "wazuh-wui"
WAZUH_PASS = "wazuh-wui"

OPENSEARCH_URL = "https://192.168.1.14:9200"
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "admin"

# ============ إعدادات SSH متعددة ============
SSH_CONNECTIONS = {
    "wazuh-server": {
        "host": "192.168.1.14",
        "user": "wazuh-user",
        "pass": "wazuh",
        "os": "linux"
    },
    "LAPTOP-P1MJQTH6": {
        "host": "172.20.10.2",
        "user": "hp",
        "pass": "admin",
        "os": "windows"
    }
}

# ============ قائمة Velociraptor Clients ============
VELOCIRAPTOR_CLIENTS = [
    {"client_id": "C.171041c2295aaee0", "hostname": "wazuh-server", "os": "linux", "ip": "192.168.1.14", "version": "0.77.1"},
    {"client_id": "C.b395517bfd021370", "hostname": "LAPTOP-P1MJQTH6", "os": "windows", "ip": "172.20.10.2", "version": "0.77.1"}
]

# ============ Telegram ============
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"

# ============ Custom CSS ============
CUSTOM_CSS = """
<style>
/* ============ PurpleOps Pro - Professional UI System ============ */

/* ===== Global Styles ===== */
.stApp {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f172a 100%);
    color: #e2e8f0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ===== Typography ===== */
h1, h2, h3, h4, h5, h6 {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

h1 {
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    text-shadow: 0 0 30px rgba(96, 165, 250, 0.3);
    animation: gradientShift 8s ease infinite;
    background-size: 200% 200%;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ===== Metric Cards - Glassmorphism ===== */
.metric-card {
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(96, 165, 250, 0.2);
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.1), transparent);
    transition: left 0.6s ease;
}

.metric-card:hover::before {
    left: 100%;
}

.metric-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: rgba(96, 165, 250, 0.6);
    box-shadow: 0 20px 60px rgba(96, 165, 250, 0.3);
}

/* ===== Status Badges ===== */
.status-badge {
    display: inline-flex;
    align-items: center;
    padding: 6px 16px;
    border-radius: 24px;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.status-badge:hover {
    transform: scale(1.05);
}

.status-success {
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.4);
    box-shadow: 0 0 20px rgba(34, 197, 94, 0.2);
}

.status-danger {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.4);
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
}

.status-warning {
    background: rgba(234, 179, 8, 0.15);
    color: #eab308;
    border: 1px solid rgba(234, 179, 8, 0.4);
    box-shadow: 0 0 20px rgba(234, 179, 8, 0.2);
}

/* ===== Buttons ===== */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    color: white;
    border: none;
    padding: 14px 28px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: translate(-50%, -50%);
    transition: width 0.6s ease, height 0.6s ease;
}

.stButton > button:hover::before {
    width: 300px;
    height: 300px;
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.6);
}

.stButton > button:active {
    transform: translateY(-1px);
}

/* ===== Sidebar ===== */
.css-1d391kg {
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(96, 165, 250, 0.2);
}

/* ===== Alert Boxes ===== */
.alert-box {
    background: rgba(239, 68, 68, 0.1);
    border-left: 4px solid #ef4444;
    padding: 16px;
    margin: 12px 0;
    border-radius: 8px;
    backdrop-filter: blur(10px);
    animation: slideInLeft 0.5s ease;
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* ===== Custom Divider ===== */
.custom-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #3b82f6, #8b5cf6, transparent);
    margin: 32px 0;
    border-radius: 2px;
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% { opacity: 0.5; }
    50% { opacity: 1; }
    100% { opacity: 0.5; }
}

/* ===== Risk Level Colors ===== */
.risk-low { color: #22c55e; font-weight: 600; }
.risk-medium { color: #eab308; font-weight: 600; }
.risk-high { color: #f97316; font-weight: 600; }
.risk-critical { 
    color: #ef4444; 
    font-weight: 700;
    text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}

/* ===== Expander Styling ===== */
.streamlit-expanderHeader {
    background: rgba(30, 41, 59, 0.5);
    border-radius: 8px;
    padding: 12px;
    transition: all 0.3s ease;
}

.streamlit-expanderHeader:hover {
    background: rgba(30, 41, 59, 0.8);
}

/* ===== Code Blocks ===== */
.stCodeBlock {
    background: rgba(15, 23, 42, 0.8);
    border-radius: 8px;
    border: 1px solid rgba(96, 165, 250, 0.2);
    padding: 16px;
}

/* ===== Loading Spinner ===== */
[data-testid="stSpinner"] > div {
    border-color: rgba(96, 165, 250, 0.3);
    border-top-color: #3b82f6;
}

/* ===== Progress Bar ===== */
.stProgress > div > div {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    border-radius: 8px;
    animation: progressPulse 2s ease infinite;
}

@keyframes progressPulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

/* ===== Selectbox & Input ===== */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(96, 165, 250, 0.3);
    border-radius: 8px;
    color: #e2e8f0;
    transition: all 0.3s ease;
}

.stSelectbox > div > div:hover,
.stTextInput > div > div > input:hover {
    border-color: rgba(96, 165, 250, 0.6);
}

.stSelectbox > div > div:focus,
.stTextInput > div > div > input:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

/* ===== Checkbox ===== */
.stCheckbox > label {
    color: #e2e8f0;
}

/* ===== Success/Error Messages ===== */
.stSuccess {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 8px;
}

.stError {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 8px;
}

.stWarning {
    background: rgba(234, 179, 8, 0.1);
    border: 1px solid rgba(234, 179, 8, 0.3);
    border-radius: 8px;
}

.stInfo {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 8px;
}

/* ===== Animations ===== */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 5px rgba(96, 165, 250, 0.5); }
    50% { box-shadow: 0 0 20px rgba(96, 165, 250, 0.8); }
}

/* ===== Scrollbar ===== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.5);
}

::-webkit-scrollbar-thumb {
    background: rgba(96, 165, 250, 0.5);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(96, 165, 250, 0.8);
}

/* ===== Responsive Design ===== */
@media (max-width: 768px) {
    h1 {
        font-size: 2rem !important;
    }
    
    .metric-card {
        padding: 16px;
    }
}
</style>
"""

# ============ دوال مساعدة ============
def execute_ssh(command, timeout=15, target="wazuh-server"):
    conn = SSH_CONNECTIONS.get(target, SSH_CONNECTIONS["wazuh-server"])
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(conn["host"], username=conn["user"], password=conn["pass"], timeout=timeout, banner_timeout=timeout, auth_timeout=timeout)
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        client.close()
        return output.strip(), error.strip()
    except Exception as e:
        return None, str(e)

@st.cache_resource
def get_wazuh_token():
    url = f"{WAZUH_API_URL}/security/user/authenticate"
    response = requests.get(url, auth=(WAZUH_USER, WAZUH_PASS), verify=False, timeout=10)
    return response.json()['data']['token']

@st.cache_data(ttl=30)
def get_agents(token):
    url = f"{WAZUH_API_URL}/agents"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers, verify=False, timeout=10)
    return response.json()['data']['affected_items']

def search_alerts(technique_id, minutes=5, rule_id=None):
    url = f"{OPENSEARCH_URL}/wazuh-alerts-*/_search"
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=minutes)
    must_conditions = [{"range": {"timestamp": {"gte": past.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), "lte": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}}}]
    if rule_id:
        must_conditions.append({"term": {"rule.id": rule_id}})
    else:
        must_conditions.append({"match": {"rule.mitre.id": technique_id}})
    query = {"query": {"bool": {"must": must_conditions}}, "size": 10, "sort": [{"timestamp": {"order": "desc"}}]}
    try:
        response = requests.post(url, json=query, auth=HTTPBasicAuth(OPENSEARCH_USER, OPENSEARCH_PASS), verify=False, timeout=10)
        if response.status_code == 200:
            return response.json().get('hits', {}).get('hits', [])
    except Exception as e:
        print(f"OpenSearch error: {e}")
    return []

def get_recent_alerts(minutes=30):
    url = f"{OPENSEARCH_URL}/wazuh-alerts-*/_search"
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=minutes)
    query = {"query": {"range": {"timestamp": {"gte": past.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), "lte": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}}}, "sort": [{"timestamp": {"order": "desc"}}], "size": 50}
    try:
        response = requests.post(url, json=query, auth=(OPENSEARCH_USER, OPENSEARCH_PASS), verify=False, timeout=10)
        if response.status_code == 200:
            return response.json()['hits']['hits']
    except:
        pass
    return []

def send_telegram_message(message, parse_mode="HTML"):
    if not TELEGRAM_ENABLED or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False, "Telegram not configured"
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": parse_mode}
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True, "Message sent"
        return False, f"Error: {response.text}"
    except Exception as e:
        return False, str(e)

def send_scan_summary(results, coverage, scan_time):
    detected = sum(1 for r in results if r['detected'])
    total = len(results)
    missed = total - detected
    if coverage >= 80: status_emoji, status_color = "🟢", "STRONG"
    elif coverage >= 60: status_emoji, status_color = "🟡", "MODERATE"
    else: status_emoji, status_color = "🔴", "CRITICAL"
    detected_list = "\n".join([f"✅ {r['id']} - {r['name'][:30]}" for r in results if r['detected']])
    missed_list = "\n".join([f"❌ {r['id']} - {r['name'][:30]}" for r in results if not r['detected']])
    message = f"""🛡️ <b>PurpleOps Pro - Scan Report</b>

📅 <b>Time:</b> {scan_time}
{status_emoji} <b>Status:</b> {status_color}

📊 <b>Results:</b>
• Coverage: <b>{coverage:.1f}%</b>
• Detected: <b>{detected}/{total}</b>
• Missed: <b>{missed}/{total}</b>

✅ <b>Detected:</b>
{detected_list if detected_list else "<i>None</i>"}

❌ <b>Missed:</b>
{missed_list if missed_list else "<i>None</i>"}

🎯 <i>PurpleOps Pro v3.1</i>"""
    return send_telegram_message(message)

def send_threat_alert(threat_name, findings):
    message = f"""🔎 <b>Threat Hunting Alert</b>
⚠️ <b>Potential Threat Detected!</b>
🎯 <b>Check:</b> {threat_name}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📋 <b>Findings:</b>
<pre>{findings[:500]}</pre>"""
    return send_telegram_message(message)

def send_active_response_alert(action, ip, reason):
    message = f"""🚨 <b>Active Response Triggered</b>
⚠️ <b>Automatic Action Taken!</b>
🔧 <b>Action:</b> {action}
🌐 <b>IP Address:</b> <code>{ip}</code>
📝 <b>Reason:</b> {reason}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    return send_telegram_message(message)
# ============ قاعدة بيانات الهجمات ============
ATTACKS_DB = {
    "T1082": {"name": "System Information Discovery", "tactic": "Discovery", "command": "whoami && hostname && uname -a && logger -t PurpleOps 'T1082: System Information Discovery executed'", "expected_rule": 100100, "risk": "LOW", "description": "Adversary gathers system information"},
    "T1078": {"name": "Valid Accounts", "tactic": "Initial Access", "command": "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 admin@127.0.0.1; logger -t PurpleOps 'T1078: Valid Accounts executed'", "expected_rule": 5710, "risk": "MEDIUM", "description": "Login attempt with default accounts"},
    "T1059": {"name": "Command and Scripting Interpreter", "tactic": "Execution", "command": "bash -c 'echo PurpleOps Test && cat /etc/passwd | head -3' && logger -t PurpleOps 'T1059: Command Interpreter executed'", "expected_rule": 100101, "risk": "MEDIUM", "description": "Execute commands via bash"},
    "T1548": {"name": "Abuse Elevation Control", "tactic": "Privilege Escalation", "command": "sudo whoami && sudo cat /etc/shadow | head -3 && logger -t PurpleOps 'T1548: Abuse Elevation Control executed'", "expected_rule": 5402, "risk": "CRITICAL", "description": "Privilege escalation via sudo"},
    "T1110": {"name": "Brute Force", "tactic": "Credential Access", "command": "for i in 1 2 3 4 5; do ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o ConnectTimeout=1 fakeuser_brute_$i@127.0.0.1; sleep 1; done; logger -t PurpleOps 'T1110: Brute Force executed'", "expected_rule": 5712, "risk": "HIGH", "description": "SSH brute force attack"},
    "T1003": {"name": "OS Credential Dumping", "tactic": "Credential Access", "command": "sudo cat /etc/shadow | head -5 && logger -t PurpleOps 'T1003: OS Credential Dumping executed'", "expected_rule": 5402, "risk": "CRITICAL", "description": "Access credential files"},
    "T1070": {"name": "Indicator Removal", "tactic": "Defense Evasion", "command": "sudo touch /tmp/purpleops_test.log && sudo rm -f /tmp/purpleops_test.log && logger -t PurpleOps 'T1070: Indicator Removal executed'", "expected_rule": 100102, "risk": "HIGH", "description": "Delete logs to hide traces"},
    "T1021": {"name": "Remote Services (SSH)", "tactic": "Lateral Movement", "command": "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 user@192.168.1.26 'echo test'; logger -t PurpleOps 'T1021: Remote Services executed'", "expected_rule": 5710, "risk": "HIGH", "description": "Lateral movement via SSH"},
    "T1048": {"name": "Exfiltration Over HTTP", "tactic": "Exfiltration", "command": "echo 'test' > /tmp/exfil.txt && curl -X POST -d @/tmp/exfil.txt http://127.0.0.1:9999 2>/dev/null; logger -t PurpleOps 'T1048: Exfiltration executed'; rm -f /tmp/exfil.txt", "expected_rule": 100103, "risk": "CRITICAL", "description": "Data exfiltration via HTTP"},
    "T1053": {"name": "Scheduled Task", "tactic": "Persistence", "command": "echo '* * * * * echo test' | sudo tee /tmp/purpleops_cron && sudo crontab -l && logger -t PurpleOps 'T1053: Scheduled Task executed' && sudo rm -f /tmp/purpleops_cron", "expected_rule": 100104, "risk": "HIGH", "description": "Create cron job for persistence"}
}