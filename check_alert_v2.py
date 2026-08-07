import requests
import urllib3
import os
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# OpenSearch API (للبحث في الـ alerts)
OPENSEARCH_URL = "https://192.168.1.15:9200"
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "admin"  # جرب "SecretPassword" إذا لم تنجح

def search_alerts():
    """البحث في OpenSearch عن alerts تتعلق بالملف المشبوه"""
    print("\n🔵 [BLUE TEAM] البحث في OpenSearch عن اكتشاف الهجوم...")
    
    # الـ endpoint الصحيح للبحث في Wazuh alerts
    url = f"{OPENSEARCH_URL}/wazuh-alerts-*/_search"
    
    # Query للبحث عن alerts تتعلق بالملف المشبوه
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"rule.groups": "syscheck"}},
                    {"wildcard": {"data.file.path": "*purpleops_test_malware*"}}
                ]
            }
        },
        "sort": [{"timestamp": {"order": "desc"}}],
        "size": 10
    }
    
    try:
        response = requests.post(
            url,
            json=query,
            auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            hits = data['hits']['hits']
            
            print(f"   ✅ تم العثور على {len(hits)} تنبيه(ات)!\n")
            
            if len(hits) > 0:
                for hit in hits:
                    source = hit['_source']
                    rule = source.get('rule', {})
                    data_info = source.get('data', {})
                    file_info = data_info.get('file', {})
                    
                    print("✅✅✅ نجاح! الـ SOC اكتشف الهجوم! ✅✅✅")
                    print(f"   🚨 Rule ID: {rule.get('id')}")
                    print(f"   📝 Description: {rule.get('description')}")
                    print(f"   📁 File Path: {file_info.get('path')}")
                    print(f"   🎯 Event: {data_info.get('event', {}).get('action')}")
                    print(f"   ⏰ Time: {source.get('timestamp')}")
                    print(f"   📊 Level: {rule.get('level')}")
                return True
            else:
                print("   ❌ لم يتم العثور على تنبيه يخص ملف المحاكاة.")
                print("   💡 تأكد من:")
                print("      1. إنشاء الملف في /etc/ على Wazuh Server")
                print("      2. انتظار 15 ثانية على الأقل")
                return False
        else:
            print(f"   ❌ فشل الاتصال بـ OpenSearch: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 R&M PurpleOps - Blue Team Verification (v2)")
    print("=" * 60)
    print("\n📋 تأكد من أنك نفّذت:")
    print("   sudo touch /etc/purpleops_test_malware.exe")
    print("   على Wazuh Server (VirtualBox)")
    
    detected = search_alerts()
    
    print("\n" + "=" * 60)
    if detected:
        print("🎯 النتيجة: الهجوم تم اكتشافه بنجاح!")
        print("   Coverage: 100% | Status: ✅ DETECTED")
    else:
        print("⚠️  النتيجة: الهجوم لم يتم اكتشافه")
        print("   Coverage: 0% | Status: ❌ NOT DETECTED")
    print("=" * 60)

if __name__ == "__main__":
    main()