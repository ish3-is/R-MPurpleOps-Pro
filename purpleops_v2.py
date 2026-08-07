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

# إعدادات SSH للتنفيذ التلقائي
SSH_HOST = "192.168.1.15"
SSH_USER = "wazuh-user"
SSH_PASS = "wazuh"  # غيّرها لكلمة مرور SSH الصحيحة

# ============ قاعدة بيانات الهجمات ============
ATTACKS_DB = {
    "T1105": {
        "name": "Ingress Tool Transfer",
        "technique": "إنشاء ملف مشبوه في /etc/",
        "command": "sudo touch /etc/purpleops_{timestamp}.exe",
        "expected_rule": 554,
        "expected_description": "File added to the system",
        "mitre_url": "https://attack.mitre.org/techniques/T1105/"
    },
    "T1078": {
        "name": "Valid Accounts - Default Accounts",
        "technique": "محاولة تسجيل دخول ببيانات خاطئة",
        "command": "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 admin@127.0.0.1",
        "expected_rule": 5710,
        "expected_description": "sshd: authentication failed",
        "mitre_url": "https://attack.mitre.org/techniques/T1078/"
    },
    "T1548": {
        "name": "Abuse Elevation Control Mechanism",
        "technique": "استخدام sudo لتنفيذ أمر بصلاحيات ROOT",
        "command": "sudo ls /root",
        "expected_rule": 5402,
        "expected_description": "Successful sudo to ROOT executed",
        "mitre_url": "https://attack.mitre.org/techniques/T1548/"
    },
    "T1110_AR": {
    "name": "Brute Force + Active Response",
    "tactic": "Credential Access",
    "technique": "محاولة brute force مع الحظر التلقائي",
    "command": "for i in {1..5}; do ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o ConnectTimeout=1 fakeuser_ar_$i@192.168.1.15; done",
    "expected_rule": 5712,
    "expected_description": "sshd: brute force trying to get access",
    "mitre_url": "https://attack.mitre.org/techniques/T1110/",
    "test_active_response": True
},
"T1070": {
    "name": "Indicator Removal on Host",
    "technique": "إنشاء ثم حذف ملف log",
    "command": "sudo touch /var/log/test_purpleops.log && sudo rm -f /var/log/test_purpleops.log",
    "expected_rule": 550,
    "expected_description": "Integrity checksum changed",
    "mitre_url": "https://attack.mitre.org/techniques/T1070/"
}
}

# ============ دوال SSH ============
def execute_ssh_command(command):
    """تنفيذ أمر على Wazuh Server عبر SSH"""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
        
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        client.close()
        
        if error and "warning" not in error.lower():
            print(f"   ⚠️  SSH Error: {error[:100]}")
        
        return output, error
    except Exception as e:
        print(f"   ❌ SSH Connection Failed: {e}")
        return None, str(e)

# ============ دوال Wazuh API ============
def get_wazuh_token():
    """الحصول على Token للمصادقة مع Wazuh API"""
    url = f"{WAZUH_API_URL}/security/user/authenticate"
    response = requests.get(url, auth=(WAZUH_USER, WAZUH_PASS), verify=False)
    response.raise_for_status()
    return response.json()['data']['token']

def get_agents(token):
    """جلب قائمة الـ Agents المتصلة"""
    url = f"{WAZUH_API_URL}/agents"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers, verify=False)
    return response.json()['data']['affected_items']

# ============ دوال OpenSearch ============
def search_alerts_by_rule(rule_id, minutes=5):
    """البحث عن alerts بناءً على Rule ID"""
    url = f"{OPENSEARCH_URL}/wazuh-alerts-*/_search"
    
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=minutes)
    
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"rule.id": rule_id}},
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
        "size": 10
    }
    
    response = requests.post(
        url, json=query,
        auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
        verify=False, timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        return data['hits']['hits']
    return []

# ============ محركات الهجوم ============
def execute_attack(attack_id):
    """تنفيذ هجوم محاكى تلقائياً عبر SSH"""
    attack = ATTACKS_DB.get(attack_id)
    if not attack:
        print(f"❌ الهجوم {attack_id} غير موجود")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    command = attack["command"].replace("{timestamp}", timestamp)
    
    print(f"\n🔴 [RED TEAM] تنفيذ الهجوم: {attack['name']}")
    print(f"    التقنية: {attack['technique']}")
    print(f"   🎯 MITRE ATT&CK: {attack_id}")
    print(f"   ⚙️  الأمر: {command}")
    
    # تنفيذ الأمر تلقائياً عبر SSH
    print(f"\n   🔄 جاري التنفيذ التلقائي عبر SSH...")
    output, error = execute_ssh_command(command)
    
    if output is not None:
        print(f"   ✅ تم تنفيذ الأمر بنجاح")
        if output.strip():
            print(f"   📤 Output: {output[:100]}")
    else:
        print(f"   ❌ فشل التنفيذ: {error}")
        return False
    
    # انتظار ظهور الـ alerts
    print(f"   ⏳ انتظار 10 ثوانٍ لظهور الـ Alerts...")
    time.sleep(10)
    
    return True

def verify_detection(attack_id):
    """التحقق من أن الـ SOC اكتشف الهجوم"""
    attack = ATTACKS_DB.get(attack_id)
    if not attack:
        return False
    
    print(f"\n🔵 [BLUE TEAM] التحقق من الاكتشاف...")
    print(f"   🎯 Rule ID المتوقع: {attack['expected_rule']}")
    print(f"   📝 الوصف المتوقع: {attack['expected_description']}")
    
    # البحث بالـ Rule ID
    hits = search_alerts_by_rule(attack['expected_rule'], minutes=5)
    
    if len(hits) > 0:
        print(f"\n✅✅✅ تم اكتشاف الهجوم! ✅✅✅")
        print(f"   📊 عدد الـ Alerts: {len(hits)}")
        
        for hit in hits[:3]:
            source = hit['_source']
            rule = source.get('rule', {})
            agent = source.get('agent', {})
            
            print(f"\n   🚨 Alert Details:")
            print(f"      Rule ID: {rule.get('id')}")
            print(f"      Description: {rule.get('description')}")
            print(f"      Level: {rule.get('level')}")
            print(f"      Agent: {agent.get('name')}")
            print(f"      Time: {source.get('timestamp')}")
        
        return True
    else:
        print(f"\n❌ لم يتم اكتشاف الهجوم!")
        print(f"   💡 اقتراحات:")
        print(f"      - تحقق من إعدادات Wazuh")
        print(f"      - تأكد من أن Rule ID صحيح")
        return False

# ============ الواجهة الرئيسية ============
def show_menu():
    print("\n" + "=" * 60)
    print("🚀 R&M PurpleOps v2 - Purple Team Automation Platform")
    print("=" * 60)
    print("\n📋 الهجمات المتاحة:")
    for i, (attack_id, attack) in enumerate(ATTACKS_DB.items(), 1):
        print(f"   {i}. [{attack_id}] {attack['name']}")
        print(f"      {attack['technique']}")
    print(f"   {len(ATTACKS_DB) + 1}. عرض الـ Agents المتصلة")
    print(f"   {len(ATTACKS_DB) + 2}. تشغيل جميع الهجمات (Full Scan)")
    print(f"   {len(ATTACKS_DB) + 3}. الخروج")
    print("=" * 60)

def run_full_scan():
    """تشغيل جميع الهجمات وعرض تقرير شامل"""
    print("\n" + "=" * 60)
    print("🚀 بدء Full Purple Team Scan")
    print("=" * 60)
    
    results = []
    for attack_id in ATTACKS_DB.keys():
        print(f"\n{'='*60}")
        print(f"🎯 Testing: {attack_id} - {ATTACKS_DB[attack_id]['name']}")
        print(f"{'='*60}")
        
        # تنفيذ الهجوم
        success = execute_attack(attack_id)
        
        if success:
            # التحقق من الاكتشاف
            detected = verify_detection(attack_id)
            results.append({
                'attack_id': attack_id,
                'name': ATTACKS_DB[attack_id]['name'],
                'detected': detected
            })
        else:
            results.append({
                'attack_id': attack_id,
                'name': ATTACKS_DB[attack_id]['name'],
                'detected': False
            })
    
    # عرض التقرير النهائي
    print("\n" + "=" * 60)
    print("📊 Purple Team Full Scan Report")
    print("=" * 60)
    
    detected_count = sum(1 for r in results if r['detected'])
    total_count = len(results)
    coverage = (detected_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n📈 Overall Coverage: {coverage:.1f}% ({detected_count}/{total_count})")
    print("\n📋 Detailed Results:")
    
    for result in results:
        status = "✅ DETECTED" if result['detected'] else "❌ NOT DETECTED"
        print(f"   {result['attack_id']} - {result['name']}: {status}")
    
    print("\n" + "=" * 60)

def main():
    print("🚀 بدء R&M PurpleOps Platform v2...")
    
    # اختبار الاتصال
    try:
        token = get_wazuh_token()
        print("✅ تم الاتصال بـ Wazuh API بنجاح")
        
        agents = get_agents(token)
        active_agents = [a for a in agents if a['status'] == 'active']
        print(f"✅ الـ Agents النشطة: {len(active_agents)}")
        
    except Exception as e:
        print(f"❌ فشل الاتصال بـ Wazuh: {e}")
        return
    
    # اختبار SSH
    print("\n🔄 اختبار الاتصال بـ SSH...")
    test_output, test_error = execute_ssh_command("echo 'SSH Test Successful'")
    if test_output:
        print("✅ تم الاتصال بـ SSH بنجاح")
    else:
        print(f"❌ فشل الاتصال بـ SSH: {test_error}")
        print("💡 تأكد من:")
        print("   1. SSH مُثبّت على Wazuh Server")
        print("   2. بيانات SSH صحيحة في الكود")
        return
    
    while True:
        show_menu()
        choice = input("\n اختر رقم الهجوم أو العملية: ").strip()
        
        if choice == str(len(ATTACKS_DB) + 3):
            print("\n👋 الخروج من المنصة. شكراً لاستخدام R&M PurpleOps!")
            break
        
        elif choice == str(len(ATTACKS_DB) + 2):
            run_full_scan()
        
        elif choice == str(len(ATTACKS_DB) + 1):
            print("\n📊 الـ Agents المتصلة:")
            for agent in agents:
                status = "🟢 Active" if agent['status'] == 'active' else "🔴 Disconnected"
                print(f"   - {agent['name']} ({agent['ip']}) | {status}")
        
        elif choice.isdigit() and 1 <= int(choice) <= len(ATTACKS_DB):
            attack_ids = list(ATTACKS_DB.keys())
            attack_id = attack_ids[int(choice) - 1]
            
            # تنفيذ الهجوم
            success = execute_attack(attack_id)
            
            if success:
                # التحقق من الاكتشاف
                detected = verify_detection(attack_id)
                
                # عرض النتيجة النهائية
                print("\n" + "=" * 60)
                print("📊 تقرير Purple Team:")
                print("=" * 60)
                print(f"   الهجوم: {ATTACKS_DB[attack_id]['name']}")
                print(f"   MITRE ATT&CK: {attack_id}")
                print(f"   MITRE URL: {ATTACKS_DB[attack_id]['mitre_url']}")
                
                if detected:
                    print(f"   ✅ Detection: DETECTED")
                    print(f"   📈 Coverage: 100%")
                    print(f"   🎯 Response: SOC Alert Triggered")
                else:
                    print(f"   ❌ Detection: NOT DETECTED")
                    print(f"    Coverage: 0%")
                    print(f"   💡 Recommendation: Create detection rule")
                
                print("=" * 60)
        
        else:
            print("❌ اختيار غير صالح. حاول مرة أخرى.")

if __name__ == "__main__":
    main()