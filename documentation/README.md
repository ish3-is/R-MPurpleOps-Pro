# 🛡️ PurpleOps Pro - Automated Purple Team Security Platform

**Version:** 3.1  
**Author:** [Your Name]  
**Date:** July 2026  
**Institution:** [University Name]  
**Supervisor:** [Supervisor Name]

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Project Objectives](#project-objectives)
3. [System Architecture](#system-architecture)
4. [Features & Capabilities](#features--capabilities)
5. [Technical Specifications](#technical-specifications)
6. [Detection Coverage](#detection-coverage)
7. [Installation Guide](#installation-guide)
8. [Usage Guide](#usage-guide)
9. [Security Considerations](#security-considerations)
10. [Performance Metrics](#performance-metrics)
11. [Academic Alignment](#academic-alignment)
12. [Conclusion](#conclusion)

---

## Executive Summary

PurpleOps Pro is an automated Purple Team security assessment platform that integrates **Wazuh SIEM**, **Velociraptor EDR**, and **MITRE ATT&CK** framework to validate Security Operations Center (SOC) detection capabilities against real-world cyber threats.

### Key Achievements:

✅ **100% MITRE ATT&CK Coverage** (10 techniques across 9 tactics)  
✅ **Real-time Threat Detection** with 90% detection rate  
✅ **Multi-platform Support** (Linux & Windows)  
✅ **Automated Active Response** with IP blocking  
✅ **Live Forensics** capabilities  
✅ **Telegram Notifications** for critical alerts  

---

## Project Objectives

1. **Automate** Purple Team exercises using MITRE ATT&CK framework
2. **Validate** SOC detection capabilities in real-time
3. **Integrate** SIEM (Wazuh) + EDR (Velociraptor) solutions
4. **Provide** actionable insights through professional dashboards
5. **Enable** automated threat response and containment

---

## System Architecture

### Components Overview


### Network Configuration

| Component | IP Address | Ports | Status |
|-----------|------------|-------|--------|
| Wazuh Manager | 192.168.1.14 | 1514, 1515, 55000, 9200 | Active |
| Streamlit Dashboard | 192.168.1.19 | 8501 | Active |
| Windows Agent (LAPTOP-P1MJQTH6) | 192.168.1.19 | Dynamic | Active (ID: 005) |
| Linux Agent (wazuh-server) | 192.168.1.14 | Dynamic | Active (ID: 000) |

---

## Features & Capabilities

### 1. Attack Simulation

- Execute **10 MITRE ATT&CK techniques** automatically
- Automated detection validation
- Real-time alert correlation
- PDF report generation
- Coverage analytics

**Supported Techniques:**
- T1082: System Information Discovery
- T1078: Valid Accounts
- T1059: Command and Scripting Interpreter
- T1548: Abuse Elevation Control
- T1110: Brute Force
- T1003: OS Credential Dumping
- T1070: Indicator Removal
- T1021: Remote Services (SSH)
- T1048: Exfiltration Over HTTP
- T1053: Scheduled Task

### 2. EDR Live Response

- **Live forensics** on Windows & Linux endpoints
- Process monitoring and analysis
- Network connection tracking
- Registry analysis (Windows)
- Custom command execution
- Real-time results display

**Forensic Capabilities:**
- System information gathering
- Running processes analysis
- Network connections inspection
- Open ports detection
- Recent logins tracking
- Suspicious file detection
- Cron jobs/Scheduled tasks review

### 3. Active Response

- **Automatic IP blocking** based on threat severity
- Manual block/unblock controls
- Real-time threat containment
- Telegram notifications for critical events
- Configurable timeout periods

**Response Rules:**
- Rule 5710: SSH Authentication Failure (Auto-block after 10 attempts)
- Rule 5712: SSH Brute Force (Auto-block after 5 attempts)
- Manual override available

### 4. Threat Intelligence

- **Sysmon integration** for advanced Windows logging
- Advanced threat hunting capabilities
- Suspicious activity detection
- IOC (Indicators of Compromise) tracking
- Real-time alerting

**Threat Hunting Checks:**
- Cryptominer detection
- SSH backdoor identification
- Suspicious SUID binaries
- Reverse shell detection
- Deleted log analysis

### 5. Multi-Page Dashboard

- **Home:** Overview and statistics
- **Attack Simulation:** Execute and validate attacks
- **EDR Live Response:** Live forensics interface
- **Live Alerts:** Real-time alert monitoring
- **Active Response:** IP management and blocking

---

## Technical Specifications

### System Requirements

**Server Requirements:**
- OS: Amazon Linux 2023
- RAM: 8GB minimum, 16GB recommended
- CPU: 4 cores minimum
- Storage: 100GB minimum
- Network: Static IP

**Client Requirements:**
- OS: Windows 11 / Linux
- RAM: 4GB minimum
- Python: 3.12+
- Network: Connectivity to server

### Software Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Core programming language |
| Streamlit | 1.28+ | Web dashboard framework |
| Wazuh | 4.14.5 | SIEM solution |
| Velociraptor | 0.77.1 | EDR solution |
| OpenSearch | 2.x | Log storage and analytics |
| Paramiko | 3.4+ | SSH library |
| Pandas | 2.0+ | Data manipulation |
| Plotly | 5.18+ | Data visualization |
| Requests | 2.31+ | HTTP library |
| FPDF | 2.7+ | PDF generation |

### Port Configuration

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Wazuh Agent Communication | 1514 | TCP/UDP | Agent-Manager communication |
| Wazuh Agent Enrollment | 1515 | TCP | Agent registration |
| Wazuh API | 55000 | TCP | REST API access |
| OpenSearch | 9200 | TCP | Search & analytics |
| Velociraptor | 8080 | TCP | Web interface |
| Velociraptor gRPC | 8443 | TCP | gRPC communication |
| Streamlit | 8501 | TCP | Dashboard access |
| SSH | 22 | TCP | Remote access |

---

## Detection Coverage

### MITRE ATT&CK Coverage: 100%

| Tactic | Technique ID | Technique Name | Detection Status |
|--------|-------------|----------------|------------------|
| **Initial Access** | T1078 | Valid Accounts | ✅ Detected |
| **Execution** | T1059 | Command and Scripting Interpreter | ✅ Detected |
| **Persistence** | T1053 | Scheduled Task/Job | ✅ Detected |
| **Privilege Escalation** | T1548 | Abuse Elevation Control | ✅ Detected |
| **Defense Evasion** | T1070 | Indicator Removal | ✅ Detected |
| **Credential Access** | T1110 | Brute Force | ✅ Detected |
| **Credential Access** | T1003 | OS Credential Dumping | ✅ Detected |
| **Discovery** | T1082 | System Information Discovery | ✅ Detected |
| **Lateral Movement** | T1021 | Remote Services (SSH) | ✅ Detected |
| **Exfiltration** | T1048 | Exfiltration Over HTTP | ✅ Detected |

**Overall Detection Rate: 90% (9/10 techniques detected)**

### Coverage by Tactic
