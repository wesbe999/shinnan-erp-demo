import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\admin_dispatch.py", encoding='utf-8', errors='ignore').readlines()
# 找 header 區塊
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if 'header' in l.lower() or 'topbar' in l.lower() or ('派工' in l and ('title' in l.lower() or 'h1' in l.lower()))]
for r in found[:10]: print(r)
