import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\buildings_admin.py", encoding='utf-8', errors='ignore').readlines()
# 找 header HTML 區塊
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'class="topbar"' in l or 'id="topbar"' in l or ('header' in l.lower() and 'class' in l.lower() and '<' in l)]
for r in found[:10]: print(r)
