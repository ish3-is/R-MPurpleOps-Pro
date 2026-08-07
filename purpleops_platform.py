import requests
import urllib3
import os
import time
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

# ============ قاعدة بيانات الهجمات (MITRE ATT&CK) ============
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
        "command": "sudo ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 admin@127.0.0.1",
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
    }
}

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

def search_alerts_by_description(keyword, minutes=5):
    """البحث عن alerts بناءً على كلمة في الوصف"""
    url = f"{OPENSEARCH_URL}/wazuh-alerts-*/_search"
    
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=minutes)
    
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"rule.description": keyword}},
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
    """تنفيذ هجوم محاكى"""
    attack = ATTACKS_DB.get(attack_id)
    if not attack:
        print(f"❌ الهجوم {attack_id} غير موجود في قاعدة البيانات")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    command = attack["command"].replace("{timestamp}", timestamp)
    
    print(f"\n🔴 [RED TEAM] تنفيذ الهجوم: {attack['name']}")
    print(f"    التقنية: {attack['technique']}")
    print(f"   🎯 MITRE ATT&CK: {attack_id}")
    print(f"   ⚙️  الأمر: {command}")
    
    # تنفيذ الأمر عبر SSH على Wazuh Server
    # (في هذه المرحلة، سننفذه يدوياً، لكن يمكن أتمتته لاحقاً)
    print(f"\n⚠️  نفّذ هذا الأمر يدوياً في Wazuh Terminal:")
    print(f"   {command}")
    print(f"\n⏳ انتظر 10 ثوانٍ ثم اضغط Enter للمتابعة...")
    input()
    
    return True

def verify_detection(attack_id):
    """التحقق من أن الـ SOC اكتشف الهجوم"""
    attack = ATTACKS_DB.get(attack_id)
    if not attack:
        return False
    
    print(f"\n🔵 [BLUE TEAM] التحقق من الاكتشاف...")
    print(f"   🎯 Rule ID المتوقع: {attack['expected_rule']}")
    print(f"   📝 الوصف المتوقع: {attack['expected_description']}")
    
    # البحث بالـ Rule ID أولاً
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
        # البحث بالوصف كبديل
        hits = search_alerts_by_description(attack['expected_description'], minutes=5)
        if len(hits) > 0:
            print(f"\n✅✅✅ تم اكتشاف الهجوم (عبر الوصف)! ✅✅✅")
            return True
        else:
            print(f"\n❌ لم يتم اكتشاف الهجوم!")
            print(f"   💡 اقتراحات:")
            print(f"      - تأكد من تنفيذ الأمر في Wazuh Terminal")
            print(f"      - انتظر 15 ثانية إضافية")
            print(f"      - تحقق من إعدادات syscheck في ossec.conf")
            return False

# ============ الواجهة الرئيسية ============
def show_menu():
    print("\n" + "=" * 60)
    print("🚀 R&M PurpleOps - Purple Team Automation Platform")
    print("=" * 60)
    print("\n📋 الهجمات المتاحة:")
    for i, (attack_id, attack) in enumerate(ATTACKS_DB.items(), 1):
        print(f"   {i}. [{attack_id}] {attack['name']}")
        print(f"      {attack['technique']}")
    print(f"   {len(ATTACKS_DB) + 1}. عرض الـ Agents المتصلة")
    print(f"   {len(ATTACKS_DB) + 2}. الخروج")
    print("=" * 60)

def main():
    print("🚀 بدء R&M PurpleOps Platform...")
    
    # اختبار الاتصال
    try:
        token = get_wazuh_token()
        print("✅ تم الاتصال بـ Wazuh API بنجاح")
        
        agents = get_agents(token)
        active_agents = [a for a in agents if a['status'] == 'active']
        print(f"✅ الـ Agents النشطة: {len(active_agents)}")
        
    except Exception as e:
        print(f" فشل الاتصال بـ Wazuh: {e}")
        return
    
    while True:
        show_menu()
        choice = input("\n اختر رقم الهجوم أو العملية: ").strip()
        
        if choice == str(len(ATTACKS_DB) + 2):
            print("\n👋 الخروج من المنصة. شكراً لاستخدام R&M PurpleOps!")
            break
        
        elif choice == str(len(ATTACKS_DB) + 1):
            print("\n📊 الـ Agents المتصلة:")
            for agent in agents:
                status = "🟢 Active" if agent['status'] == 'active' else "🔴 Disconnected"
                print(f"   - {agent['name']} ({agent['ip']}) | {status}")
        
        elif choice.isdigit() and 1 <= int(choice) <= len(ATTACKS_DB):
            attack_ids = list(ATTACKS_DB.keys())
            attack_id = attack_ids[int(choice) - 1]
            
            # تنفيذ الهجوم
            execute_attack(attack_id)
            
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
            print(" اختيار غير صالح. حاول مرة أخرى.")

if __name__ == "__main__":
    main()