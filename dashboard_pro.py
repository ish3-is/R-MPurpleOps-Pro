import streamlit as st
import requests
import urllib3
import os
import time
import paramiko
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from io import BytesIO
import base64

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# ============ إعدادات الصفحة ============
st.set_page_config(
    page_title="R&M PurpleOps Pro - Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ Telegram Notifications ============
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"

def send_telegram_message(message, parse_mode="HTML"):
    """إرسال رسالة إلى Telegram"""
    if not TELEGRAM_ENABLED or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False, "Telegram not configured"
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": parse_mode
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True, "Message sent"
        return False, f"Error: {response.text}"
    except Exception as e:
        return False, str(e)

def test_telegram_connection():
    """اختبار اتصال Telegram"""
    message = f"""🛡️ <b>PurpleOps Pro - Connection Test</b>

✅ Telegram notifications are working!

📊 <b>Configuration:</b>
• Bot: Connected
• Chat ID: <code>{TELEGRAM_CHAT_ID}</code>
• Status: Active

🚀 Ready to send security alerts!"""
    return send_telegram_message(message)

def send_scan_summary(results, coverage, scan_time):
    """إرسال ملخص Full Scan"""
    detected = sum(1 for r in results if r['detected'])
    total = len(results)
    missed = total - detected
    
    if coverage >= 80:
        status_emoji, status_color = "🟢", "STRONG"
    elif coverage >= 60:
        status_emoji, status_color = "🟡", "MODERATE"
    else:
        status_emoji, status_color = "🔴", "CRITICAL"
    
    detected_list = "\n".join([f"✅ {r['id']} - {r['name'][:30]}" for r in results if r['detected']])
    missed_list = "\n".join([f"❌ {r['id']} - {r['name'][:30]}" for r in results if not r['detected']])
    
    message = f"""🛡️ <b>PurpleOps Pro - Scan Report</b>

📅 <b>Time:</b> {scan_time}
{status_emoji} <b>Status:</b> {status_color}

📊 <b>Results:</b>
• Coverage: <b>{coverage:.1f}%</b>
• Detected: <b>{detected}/{total}</b>
• Missed: <b>{missed}/{total}</b>

✅ <b>Detected Techniques:</b>
{detected_list if detected_list else "<i>None</i>"}

❌ <b>Missed Techniques:</b>
{missed_list if missed_list else "<i>None</i>"}

🎯 <i>PurpleOps Pro v3.0</i>"""
    return send_telegram_message(message)

def send_threat_alert(threat_name, findings):
    """إرسال تنبيه Threat Hunting"""
    message = f"""🔎 <b>Threat Hunting Alert</b>

⚠️ <b>Potential Threat Detected!</b>

🎯 <b>Check:</b> {threat_name}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📋 <b>Findings:</b>
<pre>{findings[:500]}</pre>

💡 <i>Review findings and take action.</i>"""
    return send_telegram_message(message)

def send_critical_attack_alert(technique_id, name, tactic, risk):
    """إرسال تنبيه Critical Attack"""
    message = f"""🚨 <b>CRITICAL ATTACK DETECTED!</b>

🎯 <b>Technique:</b> {technique_id}
📝 <b>Name:</b> {name}
🔧 <b>Tactic:</b> {tactic}
🔥 <b>Risk:</b> {risk}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 <i>Immediate investigation recommended!</i>"""
    return send_telegram_message(message)

# ============ Custom CSS ============
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
    }
    h1, h2, h3 { color: #f1f5f9 !important; font-family: 'Inter', sans-serif; }
    h1 {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(59, 130, 246, 0.5);
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-success {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .status-danger {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .status-warning {
        background: rgba(234, 179, 8, 0.2);
        color: #eab308;
        border: 1px solid rgba(234, 179, 8, 0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(59, 130, 246, 0.4);
    }
    .css-1d391kg {
        background: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(59, 130, 246, 0.2);
    }
    .alert-box {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #3b82f6, transparent);
        margin: 30px 0;
    }
    .risk-low { color: #22c55e; }
    .risk-medium { color: #eab308; }
    .risk-high { color: #f97316; }
    .risk-critical { color: #ef4444; }
</style>
""", unsafe_allow_html=True)

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

SSH_HOST = "192.168.1.14"
SSH_USER = "wazuh-user"
SSH_PASS = "wazuh"

# ============ قائمة Velociraptor Clients ============
VELOCIRAPTOR_CLIENTS = [
    {
        "client_id": "C.171041c2295aaee0",
        "hostname": "wazuh-server",
        "os": "linux",
        "ip": "192.168.1.14",
        "version": "0.77.1"
    },
    {
        "client_id": "C.b395517bfd021370",
        "hostname": "LAPTOP-P1MJQTH6",
        "os": "windows",
        "ip": "172.20.10.2",
        "version": "0.77.1"
    }
]

# ============ قاعدة بيانات الهجمات ============
ATTACKS_DB = {
    "T1082": {
        "name": "System Information Discovery",
        "tactic": "Discovery",
        "command": "whoami && hostname && uname -a && logger -t PurpleOps 'T1082: System Information Discovery executed'",
        "expected_rule": 100100,
        "risk": "LOW",
        "description": "Adversary gathers system information"
    },
    "T1078": {
        "name": "Valid Accounts",
        "tactic": "Initial Access",
        "command": "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 admin@127.0.0.1; logger -t PurpleOps 'T1078: Valid Accounts executed'",
        "expected_rule": 5710,
        "risk": "MEDIUM",
        "description": "Login attempt with default accounts"
    },
    "T1059": {
        "name": "Command and Scripting Interpreter",
        "tactic": "Execution",
        "command": "bash -c 'echo PurpleOps Test && cat /etc/passwd | head -3' && logger -t PurpleOps 'T1059: Command Interpreter executed'",
        "expected_rule": 100101,
        "risk": "MEDIUM",
        "description": "Execute commands via bash"
    },
    "T1548": {
        "name": "Abuse Elevation Control",
        "tactic": "Privilege Escalation",
        "command": "sudo whoami && sudo cat /etc/shadow | head -3 && logger -t PurpleOps 'T1548: Abuse Elevation Control executed'",
        "expected_rule": 5402,
        "risk": "CRITICAL",
        "description": "Privilege escalation via sudo"
    },
    "T1110": {
        "name": "Brute Force",
        "tactic": "Credential Access",
        "command": "for i in 1 2 3 4 5; do ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o ConnectTimeout=1 fakeuser_brute_$i@127.0.0.1; sleep 1; done; logger -t PurpleOps 'T1110: Brute Force executed'",
        "expected_rule": 5712,
        "risk": "HIGH",
        "description": "SSH brute force attack"
    },
    "T1003": {
        "name": "OS Credential Dumping",
        "tactic": "Credential Access",
        "command": "sudo cat /etc/shadow | head -5 && logger -t PurpleOps 'T1003: OS Credential Dumping executed'",
        "expected_rule": 5402,
        "risk": "CRITICAL",
        "description": "Access credential files"
    },
    "T1070": {
        "name": "Indicator Removal",
        "tactic": "Defense Evasion",
        "command": "sudo touch /tmp/purpleops_test.log && sudo rm -f /tmp/purpleops_test.log && logger -t PurpleOps 'T1070: Indicator Removal executed'",
        "expected_rule": 100102,
        "risk": "HIGH",
        "description": "Delete logs to hide traces"
    },
    "T1021": {
        "name": "Remote Services (SSH)",
        "tactic": "Lateral Movement",
        "command": "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 user@192.168.1.26 'echo test'; logger -t PurpleOps 'T1021: Remote Services executed'",
        "expected_rule": 5710,
        "risk": "HIGH",
        "description": "Lateral movement via SSH"
    },
    "T1048": {
        "name": "Exfiltration Over HTTP",
        "tactic": "Exfiltration",
        "command": "echo 'test' > /tmp/exfil.txt && curl -X POST -d @/tmp/exfil.txt http://127.0.0.1:9999 2>/dev/null; logger -t PurpleOps 'T1048: Exfiltration executed'; rm -f /tmp/exfil.txt",
        "expected_rule": 100103,
        "risk": "CRITICAL",
        "description": "Data exfiltration via HTTP"
    },
    "T1053": {
        "name": "Scheduled Task",
        "tactic": "Persistence",
        "command": "echo '* * * * * echo test' | sudo tee /tmp/purpleops_cron && sudo crontab -l && logger -t PurpleOps 'T1053: Scheduled Task executed' && sudo rm -f /tmp/purpleops_cron",
        "expected_rule": 100104,
        "risk": "HIGH",
        "description": "Create cron job for persistence"
    }
}

# ============ دوال مساعدة ============
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

def execute_ssh(command, timeout=15, target="wazuh-server"):
    """تنفيذ أمر SSH على target محدد"""
    conn = SSH_CONNECTIONS.get(target, SSH_CONNECTIONS["wazuh-server"])
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            conn["host"],
            username=conn["user"],
            password=conn["pass"],
            timeout=timeout,
            banner_timeout=timeout,
            auth_timeout=timeout
        )
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        client.close()
        return output.strip(), error.strip()
    except Exception as e:
        return None, str(e)

def search_alerts(technique_id, minutes=5, rule_id=None):
    """Search for alerts in OpenSearch"""
    url = f"{OPENSEARCH_URL}/wazuh-alerts-*/_search"
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=minutes)
    
    must_conditions = [
        {"range": {
            "timestamp": {
                "gte": past.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "lte": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        }}
    ]
    
    if rule_id:
        must_conditions.append({"term": {"rule.id": rule_id}})
    else:
        must_conditions.append({"match": {"rule.mitre.id": technique_id}})
    
    query = {
        "query": {"bool": {"must": must_conditions}},
        "size": 10,
        "sort": [{"timestamp": {"order": "desc"}}]
    }
    
    try:
        response = requests.post(
            url, 
            json=query, 
            auth=HTTPBasicAuth(OPENSEARCH_USER, OPENSEARCH_PASS), 
            verify=False, 
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('hits', {}).get('hits', [])
    except Exception as e:
        print(f"OpenSearch error: {e}")
    return []

def get_recent_alerts(minutes=30):
    url = f"{OPENSEARCH_URL}/wazuh-alerts-*/_search"
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=minutes)
    
    query = {
        "query": {
            "range": {
                "timestamp": {
                    "gte": past.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "lte": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
            }
        },
        "sort": [{"timestamp": {"order": "desc"}}],
        "size": 50
    }
    
    try:
        response = requests.post(url, json=query, auth=(OPENSEARCH_USER, OPENSEARCH_PASS), verify=False, timeout=10)
        if response.status_code == 200:
            return response.json()['hits']['hits']
    except:
        pass
    return []

# ============ PDF Report Generator ============
def generate_pdf_report(results, coverage, scan_time):
    """توليد تقرير PDF احترافي"""
    from fpdf import FPDF
    
    class PDFReport(FPDF):
        def header(self):
            self.set_fill_color(15, 23, 42)
            self.rect(0, 0, 210, 30, 'F')
            self.set_text_color(241, 245, 249)
            self.set_font('Arial', 'B', 20)
            self.cell(0, 15, 'R&M PurpleOps - Security Assessment Report', 0, 1, 'C')
            self.set_font('Arial', 'I', 10)
            self.cell(0, 5, f'Generated: {scan_time}', 0, 1, 'C')
            self.ln(20)
        
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(100, 116, 139)
            self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Confidential', 0, 0, 'C')
        
        def section_title(self, title):
            self.set_font('Arial', 'B', 14)
            self.set_fill_color(59, 130, 246)
            self.set_text_color(255, 255, 255)
            self.cell(0, 10, title, 0, 1, 'L', True)
            self.set_text_color(0, 0, 0)
            self.ln(3)
    
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.section_title('1. Executive Summary')
    pdf.set_font('Arial', '', 11)
    
    detected = sum(1 for r in results if r['detected'])
    total = len(results)
    
    pdf.cell(0, 8, f'Total Techniques Tested: {total}', 0, 1)
    pdf.cell(0, 8, f'Detected: {detected} ({coverage:.1f}%)', 0, 1)
    pdf.cell(0, 8, f'Missed: {total - detected} ({100-coverage:.1f}%)', 0, 1)
    
    pdf.ln(5)
    if coverage >= 80:
        assessment, color = "STRONG - SOC detection effective", (34, 197, 94)
    elif coverage >= 60:
        assessment, color = "MODERATE - Some gaps", (234, 179, 8)
    else:
        assessment, color = "CRITICAL - Significant gaps", (239, 68, 68)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(*color)
    pdf.cell(0, 10, f'Overall Assessment: {assessment}', 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    pdf.add_page()
    pdf.section_title('2. Detailed Results')
    
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(59, 130, 246)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(25, 8, 'MITRE ID', 1, 0, 'C', True)
    pdf.cell(55, 8, 'Technique', 1, 0, 'C', True)
    pdf.cell(35, 8, 'Tactic', 1, 0, 'C', True)
    pdf.cell(25, 8, 'Risk', 1, 0, 'C', True)
    pdf.cell(25, 8, 'Status', 1, 0, 'C', True)
    pdf.cell(25, 8, 'Alerts', 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(0, 0, 0)
    
    for i, r in enumerate(results):
        if i % 2 == 0:
            pdf.set_fill_color(241, 245, 249)
        else:
            pdf.set_fill_color(255, 255, 255)
        
        status = 'DETECTED' if r['detected'] else 'MISSED'
        pdf.cell(25, 7, r['id'], 1, 0, 'C', True)
        pdf.cell(55, 7, r['name'][:30], 1, 0, 'L', True)
        pdf.cell(35, 7, r['tactic'][:20], 1, 0, 'L', True)
        pdf.cell(25, 7, r['risk'], 1, 0, 'C', True)
        pdf.cell(25, 7, status, 1, 0, 'C', True)
        pdf.cell(25, 7, str(r['alerts']), 1, 1, 'C', True)
    
    pdf.add_page()
    pdf.section_title('3. Detection by MITRE Tactic')
    
    tactic_stats = {}
    for r in results:
        tactic = r['tactic']
        if tactic not in tactic_stats:
            tactic_stats[tactic] = {'total': 0, 'detected': 0}
        tactic_stats[tactic]['total'] += 1
        if r['detected']:
            tactic_stats[tactic]['detected'] += 1
    
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(59, 130, 246)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 8, 'Tactic', 1, 0, 'C', True)
    pdf.cell(40, 8, 'Coverage', 1, 0, 'C', True)
    pdf.cell(40, 8, 'Detected/Total', 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    
    for tactic, stats in tactic_stats.items():
        cov = (stats['detected'] / stats['total'] * 100)
        pdf.cell(80, 7, tactic, 1, 0, 'L')
        pdf.cell(40, 7, f'{cov:.1f}%', 1, 0, 'C')
        pdf.cell(40, 7, f'{stats["detected"]}/{stats["total"]}', 1, 1, 'C')
    
    pdf.add_page()
    pdf.section_title('4. Recommendations')
    pdf.set_font('Arial', '', 11)
    
    missed = [r for r in results if not r['detected']]
    if missed:
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(239, 68, 68)
        pdf.cell(0, 8, 'Critical Gaps Detected:', 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        for r in missed:
            pdf.cell(10, 6, '-', 0, 0)
            pdf.cell(0, 6, f'{r["id"]} - {r["name"]} ({r["tactic"]})', 0, 1)
        pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'General Recommendations:', 0, 1)
    pdf.set_font('Arial', '', 10)
    for rec in [
        "Review and enhance Wazuh detection rules",
        "Enable Sysmon on Windows agents",
        "Implement correlation rules for multi-stage attacks",
        "Conduct regular Purple Team exercises",
        "Integrate threat intelligence feeds"
    ]:
        pdf.cell(10, 6, '-', 0, 0)
        pdf.multi_cell(0, 6, rec, 0, 'L')
        pdf.ln(2)
    
    pdf_bytes = pdf.output()
    return BytesIO(pdf_bytes)

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
    
    st.markdown("### 📊 Quick Stats")
    st.markdown(f"**Techniques:** {len(ATTACKS_DB)}")
    st.markdown(f"**Tactics:** {len(set(a['tactic'] for a in ATTACKS_DB.values()))}")
    st.markdown(f"**Last Scan:** {datetime.now().strftime('%H:%M')}")
    
    # ============ Telegram Section ============
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📱 Telegram Alerts")
    
    if TELEGRAM_ENABLED and TELEGRAM_BOT_TOKEN:
        st.markdown('<span class="status-badge status-success">✓ Telegram Connected</span>', unsafe_allow_html=True)
        st.markdown(f"<small style='color: #64748b;'>Chat ID: {TELEGRAM_CHAT_ID}</small>", unsafe_allow_html=True)
        
        if st.button("🔔 Test Notification", use_container_width=True):
            with st.spinner("Sending test message..."):
                success, msg = test_telegram_connection()
                if success:
                    st.success("✅ Message sent to Telegram!")
                else:
                    st.error(f"❌ {msg}")
    else:
        st.markdown('<span class="status-badge status-danger">✗ Telegram Disabled</span>', unsafe_allow_html=True)
        st.info("Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env file")

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
    st.markdown(f"""
    <div class='metric-card'>
        <div style='color: #94a3b8; font-size: 0.85rem;'>TOTAL TECHNIQUES</div>
        <div style='font-size: 2.5rem; font-weight: 800; color: #3b82f6;'>{len(ATTACKS_DB)}</div>
        <div style='color: #64748b; font-size: 0.85rem;'>MITRE ATT&CK</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div style='color: #94a3b8; font-size: 0.85rem;'>TACTICS COVERED</div>
        <div style='font-size: 2.5rem; font-weight: 800; color: #8b5cf6;'>{len(set(a['tactic'] for a in ATTACKS_DB.values()))}</div>
        <div style='color: #64748b; font-size: 0.85rem;'>Attack Categories</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='metric-card'>
        <div style='color: #94a3b8; font-size: 0.85rem;'>PLATFORM STATUS</div>
        <div style='font-size: 2.5rem; font-weight: 800; color: #22c55e;'>●</div>
        <div style='color: #64748b; font-size: 0.85rem;'>Active & Monitoring</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    if 'results' in st.session_state and st.session_state['results']:
        detected = sum(1 for r in st.session_state['results'] if r['detected'])
        total = len(st.session_state['results'])
        cov = (detected / total * 100) if total > 0 else 0
        color = '#22c55e' if cov >= 80 else '#eab308' if cov >= 60 else '#ef4444'
        
        st.markdown(f"""
        <div class='metric-card'>
            <div style='color: #94a3b8; font-size: 0.85rem;'>DETECTION RATE</div>
            <div style='font-size: 2.5rem; font-weight: 800; color: {color};'>{cov:.0f}%</div>
            <div style='color: #64748b; font-size: 0.85rem;'>{detected}/{total} Detected</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='metric-card'>
            <div style='color: #94a3b8; font-size: 0.85rem;'>DETECTION RATE</div>
            <div style='font-size: 2.5rem; font-weight: 800; color: #64748b;'>N/A</div>
            <div style='color: #64748b; font-size: 0.85rem;'>Run scan to see</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============ Attack Simulation Section ============
st.markdown("## 🎯 Attack Simulation")

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    run_full = st.button("🚀 Run Full Scan", use_container_width=True)

with col2:
    selected_attack = st.selectbox(
        "Select Single Attack",
        options=list(ATTACKS_DB.keys()),
        format_func=lambda x: f"{x} - {ATTACKS_DB[x]['name']}"
    )

with col3:
    run_single = st.button("▶️ Run", use_container_width=True)

progress_bar = st.progress(0)
status_text = st.empty()

# Execute Full Scan
if run_full:
    results = []
    total = len(ATTACKS_DB)
    
    for idx, (attack_id, attack) in enumerate(ATTACKS_DB.items()):
        status_text.markdown(f"<div class='alert-box'>🔄 <strong>Testing:</strong> {attack_id} - {attack['name']}</div>", unsafe_allow_html=True)
        
        output, error = execute_ssh(attack['command'])
        time.sleep(12)
        
        hits = search_alerts(attack_id, minutes=5, rule_id=attack['expected_rule'])
        detected = len(hits) > 0
        
        results.append({
            'id': attack_id,
            'name': attack['name'],
            'tactic': attack['tactic'],
            'risk': attack['risk'],
            'detected': detected,
            'alerts': len(hits),
            'rule': attack['expected_rule'],
            'description': attack['description']
        })
        
        # إرسال تنبيه Critical Attack
        if detected and attack['risk'] in ['CRITICAL', 'HIGH'] and TELEGRAM_ENABLED:
            send_critical_attack_alert(attack_id, attack['name'], attack['tactic'], attack['risk'])
        
        progress_bar.progress((idx + 1) / total)
    
    status_text.markdown("<div class='alert-box' style='border-color: #22c55e; background: rgba(34, 197, 94, 0.1);'>✅ <strong>Full scan completed successfully!</strong></div>", unsafe_allow_html=True)
    
    detected_count = sum(1 for r in results if r['detected'])
    coverage = (detected_count / len(results) * 100) if results else 0
    
    st.session_state['results'] = results
    st.session_state['scan_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # إرسال ملخص إلى Telegram
    if TELEGRAM_ENABLED:
        success, msg = send_scan_summary(results, coverage, st.session_state['scan_time'])
        if success:
            st.success("📱 Scan summary sent to Telegram!")
        else:
            st.warning(f"⚠️ Telegram notification failed: {msg}")

# Execute Single Attack
elif run_single:
    attack = ATTACKS_DB[selected_attack]
    
    status_text.markdown(f"<div class='alert-box'>🔄 <strong>Testing:</strong> {selected_attack} - {attack['name']}</div>", unsafe_allow_html=True)
    
    output, error = execute_ssh(attack['command'])
    time.sleep(12)
    
    hits = search_alerts(selected_attack, minutes=5, rule_id=attack['expected_rule'])
    detected = len(hits) > 0
    
    results = [{
        'id': selected_attack,
        'name': attack['name'],
        'tactic': attack['tactic'],
        'risk': attack['risk'],
        'detected': detected,
        'alerts': len(hits),
        'rule': attack['expected_rule'],
        'description': attack['description']
    }]
    
    status_text.markdown("<div class='alert-box' style='border-color: #22c55e; background: rgba(34, 197, 94, 0.1);'>✅ <strong>Test completed!</strong></div>", unsafe_allow_html=True)
    st.session_state['results'] = results
    st.session_state['scan_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # إرسال تنبيه للهجوم الحرج
    if detected and attack['risk'] in ['CRITICAL', 'HIGH'] and TELEGRAM_ENABLED:
        send_critical_attack_alert(selected_attack, attack['name'], attack['tactic'], attack['risk'])
        st.success("📱 Critical attack alert sent to Telegram!")

# ============ Results Section ============
if 'results' in st.session_state and st.session_state['results']:
    results = st.session_state['results']
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("## 📊 Assessment Results")
    
    detected_count = sum(1 for r in results if r['detected'])
    total_count = len(results)
    coverage = (detected_count / total_count * 100) if total_count > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        color = '#22c55e' if coverage >= 80 else '#eab308' if coverage >= 60 else '#ef4444'
        st.markdown(f"""
        <div class='metric-card' style='text-align: center;'>
            <div style='color: #94a3b8; font-size: 0.85rem;'>OVERALL COVERAGE</div>
            <div style='font-size: 3rem; font-weight: 800; color: {color};'>{coverage:.1f}%</div>
            <div style='color: #64748b; font-size: 0.9rem;'>{detected_count} of {total_count} techniques</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card' style='text-align: center;'>
            <div style='color: #94a3b8; font-size: 0.85rem;'>DETECTED</div>
            <div style='font-size: 3rem; font-weight: 800; color: #22c55e;'>{detected_count}</div>
            <div style='color: #64748b; font-size: 0.9rem;'>Successful Detections</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        missed = total_count - detected_count
        st.markdown(f"""
        <div class='metric-card' style='text-align: center;'>
            <div style='color: #94a3b8; font-size: 0.85rem;'>MISSED</div>
            <div style='font-size: 3rem; font-weight: 800; color: #ef4444;'>{missed}</div>
            <div style='color: #64748b; font-size: 0.9rem;'>Detection Gaps</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📈 Detection Coverage by Tactic")
    
    df = pd.DataFrame(results)
    tactic_summary = df.groupby('tactic').agg({'detected': ['sum', 'count']}).reset_index()
    tactic_summary.columns = ['Tactic', 'Detected', 'Total']
    tactic_summary['Coverage'] = (tactic_summary['Detected'] / tactic_summary['Total'] * 100)
    
    fig = px.bar(tactic_summary, x='Tactic', y='Coverage',
                 color='Coverage',
                 color_continuous_scale=[[0, '#ef4444'], [0.5, '#eab308'], [1, '#22c55e']],
                 range_y=[0, 100])
    fig.add_hline(y=80, line_dash="dash", line_color="#3b82f6", annotation_text="Target: 80%")
    fig.update_layout(
        plot_bgcolor='rgba(30, 41, 59, 0.5)',
        paper_bgcolor='rgba(15, 23, 42, 0)',
        font_color='#e2e8f0',
        title_font_size=18
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### ⚠️ Risk Level Distribution")
    
    risk_col1, risk_col2 = st.columns(2)
    
    with risk_col1:
        risk_counts = df['risk'].value_counts().reset_index()
        risk_counts.columns = ['Risk Level', 'Count']
        color_map = {'LOW': '#22c55e', 'MEDIUM': '#eab308', 'HIGH': '#f97316', 'CRITICAL': '#ef4444'}
        
        fig_pie = px.pie(risk_counts, values='Count', names='Risk Level',
                        color='Risk Level', color_discrete_map=color_map, hole=0.4)
        fig_pie.update_layout(
            plot_bgcolor='rgba(30, 41, 59, 0.5)',
            paper_bgcolor='rgba(15, 23, 42, 0)',
            font_color='#e2e8f0',
            showlegend=True
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with risk_col2:
        risk_detection = df.groupby(['risk', 'detected']).size().reset_index(name='count')
        fig_bar = px.bar(risk_detection, x='risk', y='count', color='detected',
                        barmode='group',
                        color_discrete_map={True: '#22c55e', False: '#ef4444'},
                        labels={'risk': 'Risk Level', 'count': 'Count', 'detected': 'Detected'},
                        category_orders={'risk': ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']})
        fig_bar.update_layout(
            plot_bgcolor='rgba(30, 41, 59, 0.5)',
            paper_bgcolor='rgba(15, 23, 42, 0)',
            font_color='#e2e8f0',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("### 🔥 MITRE ATT&CK Coverage Matrix")
    
    heatmap_data = []
    for result in results:
        heatmap_data.append({
            'Tactic': result['tactic'],
            'Technique': f"{result['id']} - {result['name'][:20]}",
            'Status': 1 if result['detected'] else 0
        })
    
    df_heat = pd.DataFrame(heatmap_data)
    fig_heat = px.scatter(df_heat, x='Tactic', y='Technique',
                         color='Status',
                         color_discrete_map={1: '#22c55e', 0: '#ef4444'},
                         size_max=60, labels={'Status': 'Detected'})
    fig_heat.update_traces(marker=dict(size=30, symbol='square'))
    fig_heat.update_layout(
        plot_bgcolor='rgba(30, 41, 59, 0.5)',
        paper_bgcolor='rgba(15, 23, 42, 0)',
        font_color='#e2e8f0',
        xaxis={'tickangle': -45},
        showlegend=False
    )
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.markdown("### 📋 Detailed Results")
    
    for result in results:
        status_icon = "✅" if result['detected'] else "❌"
        risk_class = f"risk-{result['risk'].lower()}"
        
        with st.expander(f"{status_icon} **{result['id']}** - {result['name']} | Risk: <span class='{risk_class}'>{result['risk']}</span>", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**MITRE ID:** {result['id']}")
                st.markdown(f"**Rule ID:** {result['rule']}")
                st.markdown(f"**Tactic:** {result['tactic']}")
            
            with col2:
                status_text = "DETECTED" if result['detected'] else "NOT DETECTED"
                st.markdown(f"**Status:** {status_text}")
                st.markdown(f"**Alerts Generated:** {result['alerts']}")
                st.markdown(f"**Risk Level:** {result['risk']}")
            
            with col3:
                st.markdown(f"**Description:**")
                st.markdown(result['description'])
                if not result['detected']:
                    st.warning("💡 Recommendation: Create or enhance detection rule")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("## 📄 Export Report")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pdf_buffer = generate_pdf_report(results, coverage, st.session_state.get('scan_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer.getvalue(),
            file_name=f"purpleops_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# ============ Live Alerts Section ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🚨 Recent Alerts (Last 30 Minutes)")

recent_alerts = get_recent_alerts(minutes=30)

if recent_alerts:
    alerts_data = []
    for hit in recent_alerts[:15]:
        source = hit['_source']
        rule = source.get('rule', {})
        agent = source.get('agent', {})
        level = rule.get('level', 0)
        
        if level >= 10:
            severity, color = "CRITICAL", "#ef4444"
        elif level >= 7:
            severity, color = "HIGH", "#f97316"
        elif level >= 4:
            severity, color = "MEDIUM", "#eab308"
        else:
            severity, color = "LOW", "#22c55e"
        
        alerts_data.append({
            'Time': source.get('timestamp', 'N/A')[:19],
            'Rule ID': rule.get('id', 'N/A'),
            'Description': rule.get('description', 'N/A'),
            'Level': level,
            'Severity': severity,
            'Agent': agent.get('name', 'N/A')
        })
    
    df_alerts = pd.DataFrame(alerts_data)
    
    for idx, row in df_alerts.iterrows():
        st.markdown(f"""
        <div style='background: rgba(30, 41, 59, 0.5); padding: 12px; margin: 5px 0; border-radius: 6px; border-left: 4px solid {
            '#ef4444' if row['Level'] >= 10 else '#f97316' if row['Level'] >= 7 else '#eab308' if row['Level'] >= 4 else '#22c55e'
        };'>
            <strong style='color: #f1f5f9;'>{row['Time']}</strong> | 
            Rule <strong>{row['Rule ID']}</strong> | 
            Level <strong>{row['Level']}</strong> | 
            <span style='color: {
                '#ef4444' if row['Level'] >= 10 else '#f97316' if row['Level'] >= 7 else '#eab308' if row['Level'] >= 4 else '#22c55e'
            }; font-weight: 600;'>{row['Severity']}</span> |
            {row['Description'][:60]}...
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No recent alerts in the last 30 minutes")

# ============ Velociraptor EDR Section ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("## 🦖 Velociraptor EDR - Live Response")

edr_col1, edr_col2 = st.columns([1, 2])

with edr_col1:
    st.markdown("### 📡 Connected Clients")
    st.success(f"✅ {len(VELOCIRAPTOR_CLIENTS)} clients registered")
    
    for client in VELOCIRAPTOR_CLIENTS:
        os_icon = "🐧" if client["os"] == "linux" else ""
        os_color = "#22c55e" if client["os"] == "linux" else "#3b82f6"
        
        st.markdown(f"""
        <div style='background: rgba(34, 197, 94, 0.1); padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 4px solid {os_color};'>
            <strong style='color: {os_color}; font-size: 1.1rem;'>{os_icon} {client["hostname"]}</strong><br>
            <small style='color: #94a3b8;'>ID: {client["client_id"]}</small><br>
            <small style='color: #64748b;'>OS: {client["os"].title()} | IP: {client["ip"]}</small><br>
            <small style='color: #64748b;'>Velociraptor: v{client["version"]}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Quick Stats")
    
    stats_commands = {
        "Total Processes": "ps aux | wc -l",
        "Active Users": "who | wc -l",
        "Open Connections": "netstat -an | grep ESTABLISHED | wc -l",
        "Disk Usage": "df -h / | tail -1 | awk '{print $5}'"
    }
    
    stats_cols = st.columns(2)
    for idx, (stat_name, cmd) in enumerate(stats_commands.items()):
        output, _ = execute_ssh(cmd, timeout=5, target="wazuh-server")
        if output:
            with stats_cols[idx % 2]:
                st.metric(stat_name, output.strip())

with edr_col2:
    st.markdown("### 🔍 Live Forensics")
    
    client_options = {c["hostname"]: c for c in VELOCIRAPTOR_CLIENTS}
    
    selected_client = st.selectbox(
        "Select Client",
        options=list(client_options.keys()),
        format_func=lambda x: f"{x} ({client_options[x]['os'].title()})"
    )
    
    client_info = client_options[selected_client]
    client_os = client_info["os"]
    
    forensic_options = {
        "linux": {
            "🖥️ System Info": "uname -a && hostname && whoami && uptime",
            "⚙️ Running Processes (Top 20)": "ps aux --sort=-%cpu | head -20",
            "🌐 Network Connections": "netstat -tulnp | grep ESTABLISHED",
            "🚪 Open Ports": "ss -tulnp",
            "👤 Recent Logins": "last -n 10",
            "🔍 Suspicious Files": "find /tmp /var/tmp -type f -mtime -1 2>/dev/null | head -20",
            "⏰ Cron Jobs": "for u in root $(ls /home); do echo \"=== $u ===\"; sudo -u $u crontab -l 2>/dev/null; done",
            "🔐 Sensitive Env Vars": "env | grep -iE 'pass|key|token|secret' || echo 'No sensitive vars'",
            "📦 Installed Packages (Recent)": "rpm -qa --last | head -20",
            "🛡️ Active Firewall Rules": "sudo iptables -L -n | head -30"
        },
        "windows": {
            "🖥️ System Info": "systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\" /C:\"System Type\"",
            "⚙️ Running Processes": "tasklist /FO CSV /NH",
            "🌐 Network Connections": "netstat -ano | findstr ESTABLISHED",
            "🚪 Open Ports": "netstat -ano | findstr LISTENING",
            "👤 Logged Users": "query user",
            "⏰ Scheduled Tasks": "schtasks /query /fo CSV /NH",
            "📦 Installed Software": "wmic product get name,version /format:csv",
            "🔐 Environment Variables": "set | findstr /I \"pass key token\"",
            "📁 Recent Files (Downloads)": "dir C:\\Users\\*\\Downloads\\*.* /o-d /b 2>nul",
            "🔍 Startup Programs": "reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        }
    }
    
    if client_os not in forensic_options:
        st.error(f"❌ Unsupported OS: {client_os}")
        st.stop()
    
    selected_forensic = st.selectbox(
        "Select Forensic Type",
        options=list(forensic_options[client_os].keys())
    )
    
    if st.button("🔍 Execute Forensic", use_container_width=True, type="primary"):
        with st.spinner(f"Executing {selected_forensic} on {selected_client}..."):
            command = forensic_options[client_os][selected_forensic]
            output, error = execute_ssh(command, timeout=20, target=selected_client)
            
            if output:
                st.success(f"✅ {selected_forensic} completed on {selected_client}!")
                code_lang = 'powershell' if client_os == "windows" else 'bash'
                st.code(output, language=code_lang)
            else:
                st.error(f"❌ Error: {error}")
                if client_os == "windows":
                    st.info("💡 تأكد من أن OpenSSH Server مثبت وشغال على Windows")

# Advanced Forensics
st.markdown("### 🎯 Advanced Forensics")

adv_col1, adv_col2 = st.columns(2)

with adv_col1:
    st.markdown("**Custom Command**")
    custom_command = st.text_area(
        "Enter custom forensic command",
        placeholder="e.g., find / -name '*.sh' -mtime -1 2>/dev/null",
        height=100,
        key="custom_cmd"
    )
    
    custom_target = st.selectbox(
        "Select Target",
        options=list(SSH_CONNECTIONS.keys()),
        key="custom_target"
    )
    
    if st.button("⚡ Execute Custom Command", use_container_width=True):
        if custom_command:
            with st.spinner(f"Executing on {custom_target}..."):
                output, error = execute_ssh(custom_command, timeout=30, target=custom_target)
                
                if output:
                    st.success("✅ Command executed!")
                    target_os = SSH_CONNECTIONS[custom_target]["os"]
                    code_lang = 'powershell' if target_os == "windows" else 'bash'
                    st.code(output, language=code_lang)
                else:
                    st.error(f"❌ Error: {error}")
        else:
            st.warning("⚠️ Please enter a command")

with adv_col2:
    st.markdown("**🔎 Threat Hunting - Quick Checks**")
    
    threat_checks = {
        "🦠 Check for Cryptominers": "ps aux | grep -iE 'xmrig|stratum|cryptonight|minerd' | grep -v grep",
        "🔓 Check for SSH Backdoors": "find / -name 'authorized_keys' -exec grep -l 'ssh-rsa' {} \\; 2>/dev/null",
        "🕵️ Check for Suspicious SUID": "find / -perm -4000 -type f 2>/dev/null | head -20",
        "📡 Check for Reverse Shells": "netstat -tulnp | grep -E ':(4444|5555|8888|9999)'",
        "🗑️ Check for Deleted Logs": "ls -la /var/log/ | grep -E '^-' | awk '$5 == 0 {print $NF}'"
    }
    
    selected_threat = st.selectbox(
        "Select Threat Check",
        options=list(threat_checks.keys()),
        key="threat_check"
    )
    
    if st.button("🔎 Run Threat Check", use_container_width=True):
        with st.spinner(f"Running {selected_threat}..."):
            output, _ = execute_ssh(threat_checks[selected_threat], timeout=20, target="wazuh-server")
            
            if output:
                st.warning(f"⚠️ **Findings detected:**")
                st.code(output, language='bash')
                
                # إرسال تنبيه إلى Telegram
                if TELEGRAM_ENABLED:
                    success, _ = send_threat_alert(selected_threat, output)
                    if success:
                        st.info("📱 Alert sent to Telegram!")
            else:
                st.success(f"✅ No threats detected for {selected_threat}")
# ============ Active Response Section ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("## ⚡ Active Response - Auto-Blocking")

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
    
    stats_cmd = """
    echo "Total: $(sudo grep -c 'add' /var/ossec/active-response/active-responses.log 2>/dev/null || echo 0)"
    echo "Blocked: $(sudo iptables -L -n | grep -c DROP)"
    """
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
            with col1:
                st.markdown(f"🌐 **{ip}**")
            with col2:
                if st.button("🔓", key=f"unblock_{ip}"):
                    unblock_ip(ip)
                    st.success(f"✅ {ip} unblocked!")
                    st.rerun()
    else:
        st.success("✅ No IPs blocked")
    
    st.markdown("### 🔧 Manual Block")
    manual_ip = st.text_input("IP to block", placeholder="192.168.1.100")
    
    if st.button("🚫 Block", use_container_width=True):
        if manual_ip:
            execute_ssh(f"sudo iptables -A INPUT -s {manual_ip} -j DROP", timeout=10, target="wazuh-server")
            st.success(f"✅ {manual_ip} blocked!")
            st.rerun()
# ============ Footer ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; padding: 30px; color: #64748b;'>
    <p style='font-size: 1.1rem; margin: 5px 0;'>🛡️ <strong>R&M PurpleOps Pro v3.1</strong></p>
    <p style='font-size: 0.9rem; margin: 5px 0;'>Automated Purple Team Platform + Telegram Alerts</p>
    <p style='font-size: 0.8rem; margin: 10px 0;'>Powered by Python + Wazuh + OpenSearch + Velociraptor + MITRE ATT&CK</p>
    <p style='font-size: 0.75rem; margin: 10px 0; color: #475569;'>Built with ❤️ for Security Teams</p>
</div>
""", unsafe_allow_html=True)