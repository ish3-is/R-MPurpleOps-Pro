import requests
import urllib3
import os
from dotenv import load_dotenv

# تعطيل تحذيرات الـ SSL (لأن شهادات Wazuh غالباً تكون Self-signed في البيئات التجريبية)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# تحميل المتغيرات من ملف .env (سننشئه في الخطوة التالية)
load_dotenv()

WAZUH_API_URL = os.getenv("WAZUH_API_URL", "https://192.168.1.100:55000") # غيّره لعنوان الـ Wazuh الخاص بك
WAZUH_USER = os.getenv("WAZUH_USER", "wazuh")
WAZUH_PASS = os.getenv("WAZUH_PASS", "wazuh")

def get_wazuh_token():
    """الحصول على Token للمصادقة مع Wazuh API"""
    url = f"{WAZUH_API_URL}/security/user/authenticate"
    try:
        response = requests.get(url, auth=(WAZUH_USER, WAZUH_PASS), verify=False)
        response.raise_for_status()
        token = response.json()['data']['token']
        print("✅ تم الحصول على Token بنجاح!")
        return token
    except Exception as e:
        print(f"❌ فشل الاتصال بـ Wazuh: {e}")
        return None

def get_agents(token):
    """جلب قائمة الـ Agents المتصلة"""
    url = f"{WAZUH_API_URL}/agents"
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        agents = response.json()['data']['affected_items']
        
        print(f"\n📊 عدد الـ Agents المتصلة: {len(agents)}")
        for agent in agents:
            status = "🟢 Active" if agent['status'] == 'active' else "🔴 Disconnected"
            print(f" - {agent['name']} (IP: {agent['ip']}) | Status: {status}")
            
    except Exception as e:
        print(f"❌ فشل جلب الـ Agents: {e}")

if __name__ == "__main__":
    print("🚀 بدء اختبار الاتصال بـ R&M PurpleOps...\n")
    token = get_wazuh_token()
    if token:
        get_agents(token)