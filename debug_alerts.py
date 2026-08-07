import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OPENSEARCH_URL = "https://192.168.1.15:9200"
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "admin"

print("🔍 جاري البحث عن آخر alerts في Wazuh...\n")

url = f"{OPENSEARCH_URL}/wazuh-alerts-*/_search"

query = {
    "query": {"match_all": {}},
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
        
        print(f"✅ إجمالي الـ alerts في Wazuh: {total}")
        print(f"✅ عرض آخر {len(hits)} alerts:\n")
        
        for i, hit in enumerate(hits, 1):
            source = hit['_source']
            rule = source.get('rule', {})
            agent = source.get('agent', {})
            
            print(f"{i}. Rule ID: {rule.get('id')} | {rule.get('description')}")
            print(f"   Agent: {agent.get('name')} | Time: {source.get('timestamp')}")
            print(f"   Level: {rule.get('level')}")
            print()
    else:
        print(f"❌ فشل الاتصال: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
except Exception as e:
    print(f"❌ خطأ: {e}")