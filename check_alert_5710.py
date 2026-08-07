import requests
import urllib3
from datetime import datetime, timezone, timedelta

urllib3.disable_warnings()

url = "https://192.168.1.15:9200/wazuh-alerts-*/_search"
now = datetime.now(timezone.utc)
past = now - timedelta(minutes=10)

query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"rule.id": 5710}},
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
    "size": 5
}

response = requests.post(url, json=query, auth=("admin", "admin"), verify=False)
data = response.json()
total = data['hits']['total']['value']

print(f"عدد alerts 5710 في آخر 10 دقائق: {total}")

if total > 0:
    print("\nآخر alerts:")
    for hit in data['hits']['hits'][:3]:
        source = hit['_source']
        print(f"  - {source['timestamp']}")
        print(f"    Rule: {source['rule']['id']} - {source['rule']['description']}")
        print(f"    Agent: {source['agent']['name']}")
        print(f"    Data: {source.get('data', {})}")
else:
    print("\n❌ لا يوجد alert 5710 في آخر 10 دقائق!")
    print("هذا يعني أن Wazuh لا يُطلق alert عند SSH من localhost")