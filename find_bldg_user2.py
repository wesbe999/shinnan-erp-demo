import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\buildings_admin.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'login-user' in l or 'loginUser' in l or 'header-user' in l or '登入者' in l or 'userLabel' in l]
for r in found[:10]: print(r)
