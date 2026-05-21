import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\buildings_admin.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'phone' in l.lower() and ('modal' in l.lower() or 'detail' in l.lower() or 'building.' in l)]
for r in found[:10]: print(r)
