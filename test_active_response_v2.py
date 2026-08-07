import paramiko
import time

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
    print("\n🔴 [RED TEAM] تنفيذ Brute Force Attack (3 محاولات)...")
    
    for i in range(3):
        print(f"   [{i+1}/3] محاولة SSH بمستخدم fakeuser_{i}...")
        output, error = execute_ssh(
            f"ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o ConnectTimeout=1 fakeuser_{i}@192.168.1.15"
        )
        time.sleep(1)
    
    # الخطوة 2: انتظار الحظر
    print("\n⏳ انتظار 15 ثانية لتفعيل الحظر...")
    time.sleep(15)
    
    # الخطوة 3: التحقق من الحظر
    print("\n🔵 [BLUE TEAM] التحقق من الحظر التلقائي...")
    
    output, _ = execute_ssh("sudo iptables -L -n | grep DROP")
    
    if "192.168.1.19" in output or "192.168.1" in output:
        print("\n✅✅✅ Active Response يعمل! ✅✅✅")
        print("   📋 قواعد الحظر:")
        for line in output.split('\n'):
            if 'DROP' in line:
                print(f"      {line.strip()}")
    else:
        print("\n❌ لم يتم العثور على حظر")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_active_response()