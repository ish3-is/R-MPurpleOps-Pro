import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OPENSEARCH_URL = "https://192.168.1.15:9200"
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "admin"

print("🔍 البحث عن أي alert يتعلق بـ syscheck (مراقبة الملفات)...\n")

url = f"{OPENSEARCH_URL}/wazuh-alerts-*/_search"

# بحث أوسع: أي alert يحتوي على كلمة syscheck في rule.groups
query = {
    "query": {
        "match": {"rule.groups": "syscheck"}
    },
    "sort": [{"timestamp": {"order": "desc"}}],
    "size": 5
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
        
        print(f"✅ إجمالي alerts الـ syscheck: {total}")
        
        if len(hits) > 0:
            print("\n📋 آخر 5 alerts للـ syscheck:\n")
            for i, hit in enumerate(hits, 1):
                source = hit['_source']
                rule = source.get('rule', {})
                data_info = source.get('data', {})
                
                print(f"{i}. Rule ID: {rule.get('id')} | {rule.get('description')}")
                print(f"   File: {data_info.get('file', {}).get('path', 'N/A')}")
                print(f"   Event: {data_info.get('event', {}).get('action', 'N/A')}")
                print(f"   Time: {source.get('timestamp')}")
                print()
        else:
            print("❌ لا توجد alerts للـ syscheck حتى الآن.")
            print("💡 انتظر 30 ثانية أخرى وجرب مرة ثانية.")
    else:
        print(f"❌ فشل الاتصال: {response.status_code}")
        
except Exception as e:
    print(f"❌ خطأ: {e}")