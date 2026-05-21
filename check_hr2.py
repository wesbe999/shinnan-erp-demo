import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\hr_admin.py", encoding='utf-8', errors='ignore').readlines()
# 找登出/logout
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'logout' in l.lower() or '登出' in l]
for r in found[:15]: print(r)
