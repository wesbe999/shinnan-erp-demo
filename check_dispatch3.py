import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\admin_dispatch.py", encoding='utf-8', errors='ignore').readlines()
# 找 body 最後的結構
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if '</body>' in l or 'toolbar' in l.lower() or ('button' in l and ('整理' in l or '新增' in l or 'toolbar' in l.lower()))]
for r in found[:20]: print(r)
