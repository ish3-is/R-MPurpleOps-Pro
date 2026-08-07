import requests
import urllib3
import os
import time
import subprocess
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

WAZUH_API_URL = os.getenv("WAZUH_API_URL")
WAZUH_USER = os.getenv("WAZUH_USER")
WAZUH_PASS = os.getenv("WAZUH_PASS")

def get_token():
    """الحصول على Token"""
    url = f"{WAZUH_API_URL}/security/user/authenticate"
    response = requests.get(url, auth=(WAZUH_USER, WAZUH_PASS), verify=False)
    return response.json()['data']['token']

def simulate_attack():
    """محاكاة هجوم: إنشاء ملف مشبوه (T1105 - Ingress Tool Transfer)"""
    print("\n🔴 [RED TEAM] بدء محاكاة الهجوم...")
    print("   الهجوم: إنشاء ملف مشبوه باسم mimikatz_test.exe")
    print("   التقنية: T1105 - Ingress Tool Transfer")
    
    # محاكاة الهجوم: إنشاء ملف مشبوه في مجلد Temp
    suspicious_file = "C:\\Windows\\Temp\\purpleops_mimikatz_test.exe"
    
    try:
        # إنشاء ملف فارغ (محاكاة تنزيل أداة مشبوهة)
        with open(suspicious_file, 'w') as f:
            f.write("This is a simulated malware file for PurpleOps testing")
        
        print(f"   ✅ تم إنشاء الملف: {suspicious_file}")
        return suspicious_file
    except Exception as e:
        print(f"   ❌ فشل تنفيذ الهجوم: {e}")
        return None

def check_detection(token, agent_name="wazuh-server"):
    """التحقق من أن Wazuh اكتشف الهجوم"""
    print("\n🔵 [BLUE TEAM] التحقق من الاكتشاف في Wazuh...")
    
    # البحث في الـ Alerts خلال آخر 60 ثانية
    url = f"{WAZUH_API_URL}/alerts"
    headers = {'Authorization': f'Bearer {token}'}
    
    # فلترة البحث عن alerts تتعلق بالملف المشبوه
    params = {
        'q': f'agent.name={agent_name};data.file.path~purpleops_mimikatz',
        'sort': 'timestamp:desc',
        'limit': 10
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()
        alerts = response.json()['data']['affected_items']
        
        if len(alerts) > 0:
            print(f"   ✅ تم اكتشاف الهجوم!")
            print(f"   عدد الـ Alerts: {len(alerts)}")
            for alert in alerts[:3]:  # عرض أول 3 alerts
                print(f"   - Rule: {alert['rule']['id']} | {alert['rule']['description']}")
                print(f"     Level: {alert['rule']['level']} | Time: {alert['timestamp']}")
            return True
        else:
            print("   ❌ لم يتم اكتشاف الهجوم!")
            return False
            
    except Exception as e:
        print(f"   ❌ فشل التحقق: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 R&M PurpleOps - Purple Team Automation Platform")
    print("=" * 60)
    
    # 1. الحصول على Token
    token = get_token()
    print("\n✅ تم المصادقة مع Wazuh API")
    
    # 2. محاكاة الهجوم
    file_path = simulate_attack()
    
    if not file_path:
        print("\n❌ فشل تنفيذ الهجوم")
        return
    
    # 3. الانتظار حتى يرصد Wazuh الهجوم
    print("\n⏳ انتظار 15 ثانية لظهور الـ Alerts في Wazuh...")
    time.sleep(15)
    
    # 4. التحقق من الاكتشاف
    detected = check_detection(token)
    
    # 5. عرض النتيجة النهائية
    print("\n" + "=" * 60)
    if detected:
        print("🎯 النتيجة: الهجوم تم اكتشافه بنجاح!")
        print("   Coverage: 100% | Status: ✅ DETECTED")
    else:
        print("⚠️  النتيجة: الهجوم لم يتم اكتشافه!")
        print("   Coverage: 0% | Status: ❌ NOT DETECTED")
        print("   💡 اقتراح: تحقق من قواعد FIM أو Sysmon في Wazuh")
    print("=" * 60)
    
    # 6. تنظيف: حذف الملف المشبوه
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"\n🧹 تم حذف الملف المشبوه: {file_path}")
        except:
            pass

if __name__ == "__main__":
    main()