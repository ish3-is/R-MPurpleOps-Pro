# 🛡️ PurpleOps Pro

> **Automated Purple Team Security Assessment Platform**

PurpleOps Pro is an advanced cybersecurity assessment and security operations platform designed to combine **Purple Team attack simulation, SIEM monitoring, EDR live response, threat detection, automated active response, and security reporting** into a unified Streamlit-based dashboard.

The platform integrates **Wazuh SIEM/XDR**, **Velociraptor EDR**, **OpenSearch**, endpoint telemetry, MITRE ATT&CK mapping, automated response capabilities, and PDF reporting to provide an end-to-end security assessment environment.

<img width="1536" height="1024" alt="pp" src="https://github.com/user-attachments/assets/a6cc5b45-e34b-4234-b3ed-6231f75e3ef0" />

## 🚀 Key Features

- 🎯 **MITRE ATT&CK Attack Simulation**
- 🛡️ **Purple Team Security Assessment**
- 🚨 **Real-Time Wazuh Alert Monitoring**
- 🦖 **Velociraptor EDR Live Response**
- ⚡ **Automated Active Response**
- 🔥 **Threat Detection & Analysis**
- 🌐 **Network & Endpoint Monitoring**
- 📊 **Interactive Security Dashboard**
- 🧠 **MITRE ATT&CK Technique Mapping**
- 📄 **Automated PDF Security Reports**
- 📱 **Telegram Security Notifications**
- 🔐 **SSH-Based Remote Management**
- 📈 **Security Metrics & Detection Rate**
- 🖥️ **Windows & Linux Endpoint Visibility**

---

## 🏗️ System Architecture

<img width="1536" height="1024" alt="pp2" src="https://github.com/user-attachments/assets/32e5d43f-4287-41db-8511-ca18beee7cd2" />



## 💻 Technology Stack
<img width="1536" height="1024" alt="pp3" src="https://github.com/user-attachments/assets/307cc404-f629-4c78-8c4f-d4e73c75edbd" />

| Category | Technologies |
|---|---|
| Frontend / UI | Streamlit, Plotly, Custom CSS (Glassmorphism) |
| Backend / Logic | Python 3.12, Paramiko (SSH), Requests, Pandas |
| SIEM / XDR | Wazuh 4.14.5, Velociraptor 0.77.1 |
| Database / Search | OpenSearch 2.x |
| Endpoint Logging | Sysmon (Windows), Auditd (Linux) |
| Infrastructure | Amazon Linux 2023, Windows 11, VirtualBox |
| Reporting | FPDF (PDF Generation) |

---

## 🎯 MITRE ATT&CK Coverage
<img width="1536" height="1024" alt="pp4" src="https://github.com/user-attachments/assets/7a70b426-6f38-45ab-9f7e-51ee5131c224" />

| Tactic | Technique ID | Technique Name | Detection Status |
|---|---|---|---|
| Initial Access | T1078 | Valid Accounts | ✅ Detected |
| Execution | T1059 | Command & Scripting Interpreter | ✅ Detected |
| Persistence | T1053 | Scheduled Task / Job | ✅ Detected |
| Privilege Escalation | T1548 | Abuse Elevation Control | ✅ Detected |
| Defense Evasion | T1070 | Indicator Removal | ✅ Detected |
| Credential Access | T1110 | Brute Force | ✅ Detected |
| Credential Access | T1003 | OS Credential Dumping | ✅ Detected |
| Discovery | T1082 | System Information Discovery | ✅ Detected |
| Lateral Movement | T1021 | Remote Services (SSH) | ✅ Detected |
| Exfiltration | T1048 | Exfiltration Over Alternative Protocol | ✅ Detected |

**Overall Detection Rate:** 90% (9/10)
**MITRE ATT&CK Coverage:** 100%

---

## 📦 Prerequisites

### Server
- Amazon Linux 2023
- Minimum 4 GB RAM
- Minimum 2 vCPU
- Minimum 100 GB Storage

### Client
- Windows 11
- Modern Linux Distribution

### Software
- Python 3.10 or higher
- Wazuh 4.14.5
- Velociraptor 0.77.1
- OpenSearch 2.x
- VirtualBox

### Network

The following ports may be required depending on the deployment architecture:

- 1514
- 1515
- 55000
- 9200
- 8501

---

## 🚀 Installation & Deployment

### 1. Clone the Repository
```bash
git clone https://github.com/ish3-is/R-MPurpleOps-Pro.git
cd R-MPurpleOps-Pro
```

### 2. Create Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Upgrade pip
```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy the environment template:
```bash
cp .env.example .env
```

For Windows:
```bash
copy .env.example .env
```

Configure the required variables:
```env
WAZUH_API_URL=https://<WAZUH_SERVER_IP>:55000
WAZUH_API_USER=<WAZUH_USERNAME>
WAZUH_API_PASSWORD=<WAZUH_PASSWORD>

WAZUH_MANAGER=<WAZUH_SERVER_IP>
WAZUH_PORT=55000

OPENSEARCH_HOST=<OPENSEARCH_SERVER_IP>
OPENSEARCH_PORT=9200

VELOCIRAPTOR_HOST=<VELOCIRAPTOR_SERVER_IP>
VELOCIRAPTOR_PORT=8000

TELEGRAM_BOT_TOKEN=<TELEGRAM_BOT_TOKEN>
TELEGRAM_CHAT_ID=<TELEGRAM_CHAT_ID>
```


### 6. Verify Python Installation
```bash
python3 --version
```
Expected:
```
Python 3.10+
```

### 7. Start PurpleOps Pro
```bash
streamlit run dashboard_pro.py
```

The dashboard will normally be available at:
```
http://localhost:8501
```

---

## 🖥️ Usage Guide

### 1. Start the Dashboard
```bash
streamlit run dashboard_pro.py
```

### 2. Access the UI
Open your browser and navigate to:
```
http://localhost:8501
```

### 3. Navigate the Pages
- 🏠 **Home:** System overview, metrics, system health, and quick statistics.
- 🎯 **Attack Simulation:** Run complete or individual MITRE ATT&CK technique simulations.
- 🦖 **EDR Live Response:** Execute live forensic queries against connected endpoints.
- 🚨 **Live Alerts:** Monitor real-time security events received from Wazuh.
- ⚡ **Active Response:** View blocked IP addresses, manually block/unblock threats, and monitor active response rules.

### 🎯 Attack Simulation

The Attack Simulation module allows security teams to simulate multiple adversary techniques mapped to the MITRE ATT&CK framework.

Supported scenarios include:
- Valid Accounts
- Command & Scripting Interpreter
- Scheduled Task / Job
- Abuse Elevation Control
- Indicator Removal
- Brute Force
- OS Credential Dumping
- System Information Discovery
- Remote Services (SSH)
- Exfiltration Over Alternative Protocol

The platform maps simulated activity to the corresponding MITRE ATT&CK technique and evaluates whether the security stack successfully detected the activity.

### 🦖 EDR Live Response

The EDR Live Response module integrates with Velociraptor to provide endpoint investigation and live forensic capabilities.

Capabilities include:
- Endpoint investigation
- Process analysis
- File analysis
- System information collection
- Live forensic queries
- Endpoint visibility
- Remote investigation
- Evidence collection

### 🚨 Live Alerts

The Live Alerts module provides real-time monitoring of security events generated by Wazuh.

The dashboard can display:
- Alert severity
- Timestamp
- Source IP
- Destination
- Agent information
- Rule ID
- Rule description
- MITRE ATT&CK mapping
- Event category
- Detection status

Example workflow:
```
Endpoint Activity
       ↓
Sysmon / Auditd
       ↓
Wazuh Agent
       ↓
Wazuh Manager
       ↓
Wazuh Rules & Decoders
       ↓
OpenSearch
       ↓
PurpleOps Pro
       ↓
Real-Time Alert
```

### ⚡ Active Response

PurpleOps Pro provides automated and manual response capabilities.

Supported actions include:
- Block malicious IP
- Unblock IP
- View blocked IP addresses
- Trigger Wazuh Active Response
- Monitor active response events
- Review response logs

Example:
```
Threat Detected
      ↓
Wazuh Rule Triggered
      ↓
Threat Classification
      ↓
Active Response
      ↓
IP Blocking
      ↓
iptables
      ↓
Threat Contained
```

---

## 📊 Security Monitoring

PurpleOps Pro provides a centralized security monitoring interface containing:
- Detection metrics
- Alert statistics
- Agent status
- Threat activity
- MITRE ATT&CK coverage
- Security events
- Response actions
- Endpoint status
- Detection rate

---

## 📄 Security Reporting

The platform supports automated PDF report generation using FPDF.

Generated reports can include:
- Assessment summary
- Detected techniques
- MITRE ATT&CK mapping
- Security alerts
- Detection rate
- Response actions
- Endpoint information
- Security findings
- Assessment conclusions

---

## 📱 Telegram Notifications

PurpleOps Pro can send security notifications through Telegram.

Example workflow:
```
Security Event
      ↓
Wazuh Detection
      ↓
PurpleOps Pro
      ↓
Alert Processing
      ↓
Telegram API
      ↓
Security Notification
```

If Telegram notifications fail, verify:
```bash
nslookup api.telegram.org
```

Also verify:
- DNS configuration
- Internet connectivity
- Firewall rules
- Proxy configuration
- Telegram Bot Token
- Telegram Chat ID

---

## 📂 Project Structure

```
purpleops-pro/
├── dashboard_pro.py              # Main Streamlit application entry point
├── utils.py                      # Shared functions, API calls, and CSS
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
│
├── documentation/                # Academic and technical documentation
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── USER_MANUAL.md
│   ├── TECHNICAL_SPECIFICATIONS.md
│   ├── ABET_REPORT.md
│   ├── USE_CASES.md
│   └── screenshots/              # UI and architecture screenshots
│
└── pages/                        # Streamlit multi-page application
    ├── 1_🎯_Attack_Simulation.py
    ├── 2_🦖_EDR_Live_Response.py
    ├── 3_🚨_Live_Alerts.py
    └── 4_⚡_Active_Response.py
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|---|---|
| Wazuh API Disconnected | Verify `WAZUH_API_URL` in `.env`. Ensure port 55000 is accessible and the Wazuh manager is running. |
| Agent shows "Never connected" | Check firewall rules and ensure port 1514 is allowed. Verify the agent's `ossec.conf` contains the correct Wazuh manager IP. |
| Telegram Notifications Fail | Verify DNS and network connectivity. Run `nslookup api.telegram.org` and verify the Telegram Bot Token and Chat ID. |
| Active Response not blocking | Ensure the Wazuh manager has the required privileges to execute the configured response command. |
| OpenSearch Connection Failed | Verify the OpenSearch service, hostname, port 9200, and network connectivity. |
| Streamlit does not start | Activate the virtual environment and reinstall dependencies using `pip install -r requirements.txt`. |
| ModuleNotFoundError | Verify that the virtual environment is active and install the missing dependency. |
| Port 8501 already in use | Start Streamlit using another port with `streamlit run dashboard_pro.py --server.port 8502`. |

---

## 🧪 Verification Commands

**Check Python**
```bash
python3 --version
```

**Check Installed Packages**
```bash
pip list
```

**Check Network Ports**
```bash
sudo ss -tulpn
```

**Check Wazuh Manager**
```bash
sudo systemctl status wazuh-manager
```

**Check Wazuh Indexer**
```bash
sudo systemctl status wazuh-indexer
```

**Check Wazuh Dashboard**
```bash
sudo systemctl status wazuh-dashboard
```

**Check Wazuh Logs**
```bash
sudo tail -f /var/ossec/logs/ossec.log
```

**Check Active Response Logs**
```bash
sudo tail -f /var/ossec/logs/active-responses.log
```

**Check Streamlit**
```bash
streamlit run dashboard_pro.py
```

**Test Local Dashboard**
```bash
curl http://localhost:8501
```

---

## 🔐 Security Considerations

For production deployments:
- Never hard-code credentials.
- Never commit `.env` to Git.
- Use strong Wazuh API credentials.
- Restrict management ports using firewall rules.
- Use HTTPS/TLS where applicable.
- Limit SSH access to trusted sources.
- Apply least-privilege principles.
- Rotate API credentials regularly.
- Secure Telegram Bot Tokens.
- Keep Wazuh, Velociraptor, OpenSearch, and operating systems updated.
- Monitor authentication and administrative activity.
- Separate attack simulation infrastructure from production environments.

---

## 🧪 Purple Team Workflow

PurpleOps Pro follows an iterative Purple Team security workflow:
<img width="1024" height="1536" alt="pp5" src="https://github.com/user-attachments/assets/bfb265fb-70f7-4ca2-9d13-b7e267404b79" />


## 🎓 Academic Alignment

This project was developed as a cybersecurity capstone project with alignment to academic and professional learning outcomes.

### ABET Student Outcomes
- SO1: Complex Problem Analysis
- SO2: Design & Implementation
- SO3: Effective Communication
- SO4: Professional Ethics
- SO6: Cybersecurity Theory Application

### NCAAA Learning Outcomes
- K1/K2: Cybersecurity Fundamentals & Tools
- S1/S2: Technical & Analytical Skills
- V1/V2: Professional Ethics & Social Responsibility

---

## 📈 Project Objectives

The primary objectives of PurpleOps Pro are:
- Build an integrated Purple Team security assessment platform.
- Simulate real-world MITRE ATT&CK techniques.
- Evaluate security monitoring and detection capabilities.
- Integrate SIEM and EDR technologies.
- Provide live endpoint investigation.
- Automate threat containment.
- Measure security detection effectiveness.
- Map security events to MITRE ATT&CK.
- Generate professional security assessment reports.
- Provide an academic and practical cybersecurity laboratory environment.

---

## 🧩 Core Components

| Component | Purpose |
|---|---|
| PurpleOps Pro | Central security assessment dashboard |
| Streamlit | Web-based user interface |
| Wazuh | SIEM/XDR and security monitoring |
| Velociraptor | EDR and digital forensic investigation |
| OpenSearch | Security event indexing and search |
| Sysmon | Windows endpoint telemetry |
| Auditd | Linux audit logging |
| Paramiko | SSH-based remote operations |
| Requests | API communication |
| Pandas | Data processing and analysis |
| Plotly | Interactive visualization |
| FPDF | PDF report generation |
| iptables | Network-level threat blocking |
| Telegram Bot API | Security notifications |

---

## 📊 Detection Performance

Current assessment results:

```
MITRE ATT&CK Techniques Evaluated: 10
Successfully Detected:              9
Overall Detection Rate:             90%
MITRE ATT&CK Coverage:              100%
```

Detection rate represents the number of evaluated techniques successfully detected during the assessment. ATT&CK coverage represents the breadth of mapped tactics and techniques included in the assessment scope.

---

## 🛠️ Development Environment

**Operating System:**
- Amazon Linux 2023
- Windows 11

**Virtualization:**
- Oracle VirtualBox

**Programming Language:**
- Python 3.12

**Web Framework:**
- Streamlit

**Security Platforms:**
- Wazuh 4.14.5
- Velociraptor 0.77.1

**Search / Analytics:**
- OpenSearch 2.x

**Endpoint Telemetry:**
- Sysmon
- Auditd

---

## 📝 Documentation

The project documentation is organized under:
```
documentation/
```

Available documentation includes:
- README.md
- ARCHITECTURE.md
- USER_MANUAL.md
- TECHNICAL_SPECIFICATIONS.md
- ABET_REPORT.md
- USE_CASES.md
- screenshots/

---

## 🤝 Contribution

Contributions, improvements, security testing, and educational feedback are welcome.

Before submitting changes:
```bash
git pull
git checkout -b feature/your-feature
```

After completing your changes:
```bash
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```

Then create a Pull Request.

---

## ⚠️ Disclaimer

PurpleOps Pro is intended strictly for:
- Authorized security assessments
- Cybersecurity education
- Academic research
- Controlled laboratory environments
- Purple Team exercises
- Defensive security testing

**Only perform attack simulations against systems and environments for which you have explicit authorization.**

---

## 👤 Author & Contact

**Developed by:** Meshal Jathmi & Remas Al-Qahtani
**University:** [King Khaled University] & [Bisha University]
**Email:** [mesh.jth@gmail.com] & [rta127@gmail.com]
**LinkedIn:** www.linkedin.com/in/meshjth & www.linkedin.com/in/remas-alqahtani-1674b33a8/
**GitHub:** https://github.com/ish3-is

---

## 📜 License

This project is licensed under the MIT License.

See the `LICENSE` file for more information.

---

<div align="center">

### 🛡️ PurpleOps Pro
**Automated Purple Team Security Assessment Platform**

*Simulate. Detect. Investigate. Respond. Improve.*

Built with ❤️ for the Cybersecurity Community.

</div>
