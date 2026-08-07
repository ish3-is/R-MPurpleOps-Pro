import requests
import urllib3
import os
import time
import paramiko
import yaml
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from typing import List, Dict, Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# ============ إعدادات الاتصال ============
WAZUH_API_URL = os.getenv("WAZUH_API_URL", "https://192.168.1.15:55000")
WAZUH_USER = os.getenv("WAZUH_USER", "api-user")
WAZUH_PASS = os.getenv("WAZUH_PASS", "PurpleOps2026!")

OPENSEARCH_URL = "https://192.168.1.15:9200"
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "admin"

SSH_HOST = "192.168.1.15"
SSH_USER = "wazuh-user"
SSH_PASS = "wazuh"

ATOMIC_RED_TEAM_PATH = "/opt/atomic-red-team"

# ============ قاعدة بيانات الـ Atomic Tests ============
ATOMIC_TESTS_DB = {
    "T1082": {
        "name": "System Information Discovery",
        "tactic": "Discovery",
        "description": "An adversary may attempt to get detailed information about the operating system and hardware",
        "atomic_tests": [
            {
                "name": "System Information Discovery",
                "executor": "bash",
                "command": "uname -a && cat /etc/os-release && whoami && hostname",
                "expected_rules": [550, 571]
            }
        ]
    },
    "T1078": {
        "name": "Valid Accounts",
        "tactic": "Initial Access",
        "description": "Adversaries may use valid accounts to gain initial access",
        "atomic_tests": [
            {
                "name": "SSH Login Attempt with Invalid User",
                "executor": "bash",
                "command": "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 invalid_user_12345@127.0.0.1",
                "expected_rules": [5710, 5712]
            }
        ]
    },
    "T1059": {
        "name": "Command and Scripting Interpreter",
        "tactic": "Execution",
        "description": "Adversaries may abuse command and script interpreters to execute commands",
        "atomic_tests": [
            {
                "name": "Execute Bash Commands",
                "executor": "bash",
                "command": "bash -c 'echo Atomic Red Team Test && cat /etc/passwd | head -5'",
                "expected_rules": [550, 571]
            },
            {
                "name": "Execute Python Commands",
                "executor": "bash",
                "command": "python3 -c 'import os; print(\"Python execution test\"); print(os.getcwd())'",
                "expected_rules": [550, 571]
            }
        ]
    },
    "T1548": {
        "name": "Abuse Elevation Control Mechanism",
        "tactic": "Privilege Escalation",
        "description": "Adversaries may circumvent mechanisms designed to control elevate privileges",
        "atomic_tests": [
            {
                "name": "Sudo Execution",
                "executor": "bash",
                "command": "sudo whoami && sudo cat /etc/shadow | head -3",
                "expected_rules": [5402, 5403]
            }
        ]
    },
    "T1110": {
        "name": "Brute Force",
        "tactic": "Credential Access",
        "description": "Adversaries may use brute force techniques to gain access to accounts",
        "atomic_tests": [
            {
                "name": "SSH Brute Force Simulation",
                "executor": "bash",
                "command": "for i in {1..5}; do ssh -o StrictHostKeyChecking=no -o ConnectTimeout=1 fakeuser$i@127.0.0.1; done",
                "expected_rules": [5710, 5712]
            }
        ]
    },
    "T1003": {
        "name": "OS Credential Dumping",
        "tactic": "Credential Access",
        "description": "Adversaries may attempt to dump credentials to obtain material",
        "atomic_tests": [
            {
                "name": "Access /etc/shadow",
                "executor": "bash",
                "command": "sudo cat /etc/shadow | head -5",
                "expected_rules": [5402, 550]
            },
            {
                "name": "Access /etc/passwd",
                "executor": "bash",
                "command": "cat /etc/passwd",
                "expected_rules": [550, 571]
            }
        ]
    },
    "T1070": {
        "name": "Indicator Removal on Host",
        "tactic": "Defense Evasion",
        "description": "Adversaries may delete or modify artifacts associated with their behaviors",
        "atomic_tests": [
            {
                "name": "Clear System Logs",
                "executor": "bash",
                "command": "sudo touch /tmp/test_log.txt && sudo rm -f /tmp/test_log.txt",
                "expected_rules": [550, 554]
            }
        ]
    },
    "T1021": {
        "name": "Remote Services",
        "tactic": "Lateral Movement",
        "description": "Adversaries may use remote services to move laterally",
        "atomic_tests": [
            {
                "name": "SSH Connection Attempt",
                "executor": "bash",
                "command": "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 wazuh-user@192.168.1.26 'echo test'",
                "expected_rules": [5710, 5712]
            }
        ]
    },
    "T1048": {
        "name": "Exfiltration Over Alternative Protocol",
        "tactic": "Exfiltration",
        "description": "Adversaries may steal data by exfiltrating over a different protocol",
        "atomic_tests": [
            {
                "name": "HTTP Exfiltration Simulation",
                "executor": "bash",
                "command": "echo 'test data' > /tmp/exfil_test.txt && curl -X POST -d @/tmp/exfil_test.txt http://127.0.0.1:9999 2>/dev/null; rm -f /tmp/exfil_test.txt",
                "expected_rules": [550, 1002]
            }
        ]
    },
    "T1053": {
        "name": "Scheduled Task/Job",
        "tactic": "Persistence",
        "description": "Adversaries may abuse task scheduling functionality to facilitate initial or recurring execution",
        "atomic_tests": [
            {
                "name": "Cron Job Creation",
                "executor": "bash",
                "command": "echo '* * * * * echo test' | sudo tee /tmp/test_cron && sudo rm -f /tmp/test_cron",
                "expected_rules": [554, 550]
            }
        ]
    }
}

# ============ دوال الاتصال ============
def get_wazuh_token():
    """الحصول على Token للمصادقة مع Wazuh API"""
    url = f"{WAZUH_API_URL}/security/user/authenticate"
    response = requests.get(url, auth=(WAZUH_USER, WAZUH_PASS), verify=False)
    response.raise_for_status()
    return response.json()['data']['token']

def execute_ssh_command(command, timeout=15):
    """تنفيذ أمر على Wazuh Server عبر SSH"""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=timeout)
        
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        client.close()
        return output.strip(), error.strip()
    except Exception as e:
        return None, str(e)

def search_alerts_in_window(rule_ids: List[int], minutes=5):
    """البحث عن alerts لـ rules معينة في إطار زمني"""
    url = f"{OPENSEARCH_URL}/wazuh-alerts-*/_search"
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=minutes)
    
    query = {
        "query": {
            "bool": {
                "must": [
                    {"terms": {"rule.id": rule_ids}},
                    {"range": {
                        "timestamp": {
                            "gte": past.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                            "lte": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        }
                    }}
                ]
            }
        },
        "sort": [{"timestamp": {"order": "desc"}}],
        "size": 20
    }
    
    try:
        response = requests.post(
            url, json=query,
            auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
            verify=False, timeout=10
        )
        if response.status_code == 200:
            return response.json()['hits']['hits']
    except:
        pass
    return []

def search_recent_alerts(minutes=2):
    """البحث عن آخر alerts في إطار زمني"""
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
        "size": 30
    }
    
    try:
        response = requests.post(
            url, json=query,
            auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
            verify=False, timeout=10
        )
        if response.status_code == 200:
            return response.json()['hits']['hits']
    except:
        pass
    return []

# ============ Atomic Red Team Executor ============
def load_atomic_test(technique_id: str) -> Optional[Dict]:
    """تحميل atomic test من قاعدة البيانات"""
    return ATOMIC_TESTS_DB.get(technique_id)

def execute_atomic_test(technique_id: str, test_index: int = 0, start_time: datetime = None):
    """تنفيذ atomic test واحد"""
    test_data = load_atomic_test(technique_id)
    
    if not test_data:
        print(f"❌ Technique {technique_id} غير موجود في قاعدة البيانات")
        return None
    
    if test_index >= len(test_data['atomic_tests']):
        print(f"❌ Test index {test_index} غير صالح")
        return None
    
    atomic_test = test_data['atomic_tests'][test_index]
    
    print(f"\n{'='*70}")
    print(f"🎯 Atomic Test: {test_data['name']}")
    print(f"   MITRE: {technique_id}")
    print(f"   Tactic: {test_data['tactic']}")
    print(f"   Test: {atomic_test['name']}")
    print(f"   Executor: {atomic_test['executor']}")
    print(f"{'='*70}")
    
    # تسجيل الوقت قبل التنفيذ
    if start_time is None:
        start_time = datetime.now(timezone.utc)
    
    # تنفيذ الأمر
    command = atomic_test['command']
    print(f"\n🔴 [RED TEAM] تنفيذ الأمر:")
    print(f"   {command}")
    
    output, error = execute_ssh_command(command)
    
    if output:
        preview = output[:150].replace('\n', ' | ')
        print(f"\n   ✅ Output: {preview}...")
    elif error:
        print(f"\n   ⚠️  Error: {error[:100]}")
    else:
        print(f"\n   ⚙️  Executed (no output)")
    
    # انتظار ظهور الـ alerts
    print(f"\n   ⏳ انتظار 10 ثوانٍ لرصد الـ Alerts...")
    time.sleep(10)
    
    # التحقق من الاكتشاف
    print(f"\n🔵 [BLUE TEAM] التحقق من الاكتشاف...")
    expected_rules = atomic_test['expected_rules']
    print(f"   🎯 Expected Rules: {expected_rules}")
    
    hits = search_alerts_in_window(expected_rules, minutes=3)
    recent_alerts = search_recent_alerts(minutes=2)
    
    # تصفية alerts التي حدثت بعد بدء الهجوم
    relevant_alerts = []
    for hit in recent_alerts:
        alert_time = hit['_source'].get('timestamp', '')
        if alert_time >= start_time.strftime("%Y-%m-%dT%H:%M:%S"):
            relevant_alerts.append(hit)
    
    detected = len(hits) > 0 or len(relevant_alerts) > 0
    
    # عرض النتائج
    if detected:
        print(f"\n   ✅✅✅ تم اكتشاف Atomic Test! ✅✅✅")
        print(f"   📊 عدد الـ Alerts: {len(hits) + len(relevant_alerts)}")
        
        all_alerts = hits + relevant_alerts
        for alert in all_alerts[:3]:
            source = alert['_source']
            rule = source.get('rule', {})
            print(f"\n      🚨 Rule {rule.get('id')}: {rule.get('description')}")
            print(f"         Level: {rule.get('level')} | Time: {source.get('timestamp')}")
    else:
        print(f"\n   ❌ لم يتم اكتشاف Atomic Test!")
        print(f"   💡 الـ SOC فشل في رصد هذه التقنية")
    
    return {
        'technique_id': technique_id,
        'technique_name': test_data['name'],
        'tactic': test_data['tactic'],
        'test_name': atomic_test['name'],
        'executor': atomic_test['executor'],
        'command': command,
        'detected': detected,
        'alerts_count': len(hits) + len(relevant_alerts),
        'expected_rules': expected_rules
    }

def run_all_atomic_tests():
    """تنفيذ جميع atomic tests"""
    print("\n" + "="*70)
    print("🚀 Atomic Red Team - Full Execution")
    print("="*70)
    print(f"📅 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 عدد التقنيات: {len(ATOMIC_TESTS_DB)}")
    print(f"🖥️  الهدف: {SSH_HOST}")
    print("="*70)
    
    # اختبار الاتصال
    print("\n🔄 اختبار الاتصال...")
    output, error = execute_ssh_command("echo 'Connection Test'")
    if output:
        print("✅ SSH Connection: OK")
    else:
        print(f"❌ SSH Connection Failed: {error}")
        return
    
    try:
        token = get_wazuh_token()
        print("✅ Wazuh API: Connected")
    except Exception as e:
        print(f"❌ Wazuh API Failed: {e}")
        return
    
    print("\n⚠️  تحذير: سيتم تنفيذ جميع Atomic Tests على النظام الفعلي!")
    confirm = input("\nهل تريد المتابعة؟ (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ تم الإلغاء")
        return
    
    # تنفيذ جميع التقنيات
    results = []
    for technique_id, test_data in ATOMIC_TESTS_DB.items():
        for test_index in range(len(test_data['atomic_tests'])):
            result = execute_atomic_test(technique_id, test_index)
            if result:
                results.append(result)
            
            # انتظار بين الاختبارات
            print(f"\n   ⏸️  انتظار 5 ثوانٍ قبل الاختبار التالي...")
            time.sleep(5)
    
    # التقرير النهائي
    print_final_report(results)
    return results

def print_final_report(results: List[Dict]):
    """عرض التقرير النهائي"""
    print("\n" + "="*70)
    print("📊 Atomic Red Team - التقرير النهائي")
    print("="*70)
    
    detected_count = sum(1 for r in results if r['detected'])
    total_count = len(results)
    coverage = (detected_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n📈 Overall Detection Rate: {coverage:.1f}% ({detected_count}/{total_count})")
    
    # تحليل حسب Tactic
    tactic_analysis = {}
    for r in results:
        tactic = r['tactic']
        if tactic not in tactic_analysis:
            tactic_analysis[tactic] = {'total': 0, 'detected': 0}
        tactic_analysis[tactic]['total'] += 1
        if r['detected']:
            tactic_analysis[tactic]['detected'] += 1
    
    print("\n📊 Detection by Tactic:")
    for tactic in sorted(tactic_analysis.keys()):
        data = tactic_analysis[tactic]
        rate = (data['detected'] / data['total'] * 100) if data['total'] > 0 else 0
        print(f"   {tactic:<25s}: {rate:5.1f}% ({data['detected']}/{data['total']})")
    
    print("\n📋 Detailed Results:")
    print(f"{'Technique':<10} {'Name':<35} {'Tactic':<20} {'Status':<15} {'Alerts'}")
    print("-"*95)
    for r in results:
        status = "✅ DETECTED" if r['detected'] else "❌ MISSED"
        print(f"{r['technique_id']:<10} {r['technique_name']:<35} {r['tactic']:<20} {status:<15} {r['alerts_count']}")
    
    # تحليل الثغرات
    missed = [r for r in results if not r['detected']]
    if missed:
        print("\n⚠️  ثغرات في الـ SOC:")
        for r in missed:
            print(f"   - {r['technique_id']} - {r['technique_name']} ({r['tactic']})")
    
    print("\n💡 التوصيات:")
    if coverage < 80:
        print("   1. تحسين قواعد الاكتشاف في Wazuh")
        print("   2. تفعيل Sysmon على الأنظمة Windows")
        print("   3. إضافة Rules للـ MITRE Techniques المفقودة")
    else:
        print("   ✅ أداء SOC ممتاز! استمر في التحسين المستمر")
    
    print("\n" + "="*70)

# ============ الوضع التفاعلي ============
def interactive_mode():
    """الوضع التفاعلي"""
    print("\n" + "="*70)
    print("🎯 Atomic Red Team - Interactive Mode")
    print("="*70)
    
    print("\n📋 التقنيات المتاحة:")
    techniques = list(ATOMIC_TESTS_DB.keys())
    for i, tech_id in enumerate(techniques, 1):
        test_data = ATOMIC_TESTS_DB[tech_id]
        print(f"   {i}. [{tech_id}] {test_data['name']}")
        print(f"      Tactic: {test_data['tactic']}")
        print(f"      Tests: {len(test_data['atomic_tests'])}")
    
    print(f"\n   {len(techniques) + 1}. تشغيل جميع التقنيات")
    print(f"   {len(techniques) + 2}. الخروج")
    print("="*70)
    
    choice = input("\nاختر رقم التقنية: ").strip()
    
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(techniques):
            tech_id = techniques[choice - 1]
            test_data = ATOMIC_TESTS_DB[tech_id]
            
            print(f"\n📋 Atomic Tests لـ {tech_id}:")
            for i, test in enumerate(test_data['atomic_tests'], 1):
                print(f"   {i}. {test['name']}")
            
            test_choice = input(f"\nاختر رقم الاختبار (1-{len(test_data['atomic_tests'])}): ").strip()
            
            if test_choice.isdigit():
                test_index = int(test_choice) - 1
                if 0 <= test_index < len(test_data['atomic_tests']):
                    execute_atomic_test(tech_id, test_index)
                else:
                    print("❌ اختيار غير صالح")
            else:
                print("❌ اختيار غير صالح")
        
        elif choice == len(techniques) + 1:
            run_all_atomic_tests()
        elif choice == len(techniques) + 2:
            print("👋 الخروج")
        else:
            print("❌ اختيار غير صالح")

def main():
    print("\n" + "="*70)
    print("🛡️ R&M PurpleOps - Atomic Red Team Integration")
    print("="*70)
    print("\nهذا النظام ينفذ Atomic Tests من MITRE ATT&CK")
    print("تأكد من أنك في بيئة اختبار معزولة.\n")
    
    print("اختر الوضع:")
    print("   1. 🎯 Interactive Mode (تقنية واحدة)")
    print("   2. 🚀 Full Execution (كل التقنيات)")
    print("   3. ❌ الخروج")
    
    choice = input("\nاختر: ").strip()
    
    if choice == '1':
        interactive_mode()
    elif choice == '2':
        run_all_atomic_tests()
    elif choice == '3':
        print("👋 الخروج")
    else:
        print("❌ اختيار غير صالح")

if __name__ == "__main__":
    main()