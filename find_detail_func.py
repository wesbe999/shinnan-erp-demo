import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\buildings_admin.py", encoding='utf-8', errors='ignore').readlines()
# 找 openDetail 或 showDetail 函式
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if 'function openDetail' in l or 'function showDetail' in l or 'function showBuilding' in l or 'function openBuilding' in l]
for r in found[:10]: print(r)
