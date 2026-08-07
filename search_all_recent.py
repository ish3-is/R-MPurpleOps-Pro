import requests
import urllib3
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OPENSEARCH_URL = "https://192.168.1.15:9200"
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "admin"

print("🔍 البحث عن آخر 20 alert في آخر 5 دقائق...\n")

url = f"{OPENSEARCH_URL}/wazuh-alerts-*/_search"

# حساب وقت آخر 5 دقائق
now = datetime.utcnow()
five_min_ago = now - timedelta(minutes=5)

# صيغة التاريخ المطلوبة لـ OpenSearch
time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
query = {
    "query": {
        "range": {
            "timestamp": {
                "gte": five_min_ago.strftime(time_format),
                "lte": now.strftime(time_format)
            }
        }
    },
    "sort": [{"timestamp": {"order": "desc"}}],
    "size": 20
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
        total = data['hits']['total']['value']
        
        print(f"✅ إجمالي alerts في آخر 5 دقائق: {total}")
        
        if len(hits) > 0:
            print("\n📋 تفاصيل الـ alerts:\n")
            for i, hit in enumerate(hits, 1):
                source = hit['_source']
                rule = source.get('rule', {})
                
                print(f"{i}. Rule ID: {rule.get('id')} | Level: {rule.get('level')}")
                print(f"   Description: {rule.get('description')}")
                print(f"   Groups: {rule.get('groups', [])}")
                print(f"   Time: {source.get('timestamp')}")
                print("-" * 50)
        else:
            print("❌ لا توجد alerts في آخر 5 دقائق!")
            print(" تأكد من:")
            print("   1. إعادة تشغيل Wazuh بعد التعديل")
            print("   2. إنشاء ملف جديد في /etc/")
            print("   3. انتظار 10 ثوانٍ")
    else:
        print(f"❌ فشل الاتصال: {response.status_code}")
        
except Exception as e:
    print(f"❌ خطأ: {e}")