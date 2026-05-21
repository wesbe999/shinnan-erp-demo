import paramiko

HOST = '192.168.99.1'
PORT = 3200
USER = 'wesbe'
PASS = '@Zax129381'

def rb(cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=10)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode()
    ssh.close()
    return result

print('=== L2TP Server 狀態 ===')
print(rb('/interface l2tp-server server print'))

print('=== PPP Secret ===')
print(rb('/ppp secret print'))

print('=== PPP Profile ===')
print(rb('/ppp profile print where name=vpn-profile'))

print('=== IP Pool ===')
print(rb('/ip pool print where name=vpn-pool'))

print('=== 防火牆 L2TP 規則 ===')
print(rb('/ip firewall filter print where comment~"L2TP" or comment~"IPSec"'))
