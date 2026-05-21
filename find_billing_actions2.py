import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\billing.py", encoding='utf-8', errors='ignore').readlines()
# 找 JS 裡動態注入的 web-title-actions
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'web-title-actions' in l or ('logout' in l.lower() and 'xn-logout' in l)]
for r in found[:15]: print(r)
