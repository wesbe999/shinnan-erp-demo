import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\admin_dispatch.py", encoding='utf-8', errors='ignore').readlines()
# 找 route 函式和 html.replace 或 return
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if 'def ' in l and ('dispatch' in l.lower() or 'admin' in l.lower())]
for r in found[:10]: print(r)
