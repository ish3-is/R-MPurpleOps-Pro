import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OPENSEARCH_URL = "https://192.168.1.15:9200"
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "admin"

print("🔍 البحث عن أي alert يحتوي على كلمة 'file' في الوصف...\n")

url = f"{OPENSEARCH_URL}/wazuh-alerts-*/_search"

# بحث أوسع: أي alert يحتوي على "file" في rule.description
query = {
    "query": {
        "match": {"rule.description": "file"}
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
        total = data['hits']['total']['value']
        
        print(f"✅ إجمالي alerts المتعلقة بـ 'file': {total}")
        
        if len(hits) > 0:
            print("\n📋 آخر 10 alerts:\n")
            for i, hit in enumerate(hits, 1):
                source = hit['_source']
                rule = source.get('rule', {})
                
                print(f"{i}. Rule ID: {rule.get('id')} | {rule.get('description')}")
                print(f"   Groups: {rule.get('groups', [])}")
                print(f"   Time: {source.get('timestamp')}")
                print()
        else:
            print("❌ لا توجد alerts تحتوي على 'file' في الوصف.")
    else:
        print(f"❌ فشل الاتصال: {response.status_code}")
        
except Exception as e:
    print(f"❌ خطأ: {e}")