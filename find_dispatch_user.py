import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\admin_dispatch.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if 'replace' in l and ('USER' in l or 'user' in l or 'name' in l.lower())]
for r in found[:10]: print(r)
