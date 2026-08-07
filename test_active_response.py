import paramiko
import time
from datetime import datetime

SSH_HOST = "192.168.1.15"
SSH_USER = "wazuh-user"
SSH_PASS = "wazuh"

def execute_ssh(command, timeout=10):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=timeout)
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    client.close()
    return output.strip(), error.strip()

def test_active_response():
    print("\n" + "="*70)
    print("🛡️ اختبار Active Response - الحظر التلقائي")
    print("="*70)
    
    # الخطوة 1: تنفيذ Brute Force
    print("\n🔴 [RED TEAM] تنفيذ Brute Force Attack...")
    print("   محاولة 10 تسجيلات دخول فاشلة خلال 30 ثانية")
    
    for i in range(10):
        print(f"   [{i+1}/10] محاولة SSH بمستخدم fakeuser_{i}...")
        output, error = execute_ssh(f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=1 fakeuser_{i}@127.0.0.1")
        time.sleep(3)
    
    # الخطوة 2: انتظار الحظر
    print("\n⏳ انتظار 15 ثانية لتفعيل Active Response...")
    time.sleep(15)
    
    # الخطوة 3: التحقق من الحظر
    print("\n [BLUE TEAM] التحقق من الحظر التلقائي...")
    
    output, _ = execute_ssh("sudo iptables -L -n | grep DROP")
    
    if "DROP" in output:
        print("\n✅✅✅ Active Response يعمل! ✅✅✅")
        print("   📋 قواعد الحظر:")
        for line in output.split('\n')[:5]:
            print(f"      {line}")
        
        # الخطوة 4: اختبار أن الحظر فعّال
        print("\n🧪 اختبار: محاولة SSH بعد الحظر...")
        output, error = execute_ssh("ssh -o ConnectTimeout=3 fakeuser@127.0.0.1", timeout=5)
        
        if "Connection timed out" in error or "No route" in error:
            print("   ✅ الحظر فعّال! الاتصال مرفوض")
        else:
            print("   ⚠️  الحظر قد لا يكون فعّالاً")
    else:
        print("\n❌ Active Response لم يعمل")
        print("   💡 تأكد من:")
        print("      1. تفعيل <active-response> في ossec.conf")
        print("      2. إعادة تشغيل wazuh-manager")
        print("      3. وجود rules_id صحيحة (5710, 5712)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_active_response()