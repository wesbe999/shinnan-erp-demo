import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\billing.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'cl15j1-billing-header-actions' in l and ('{' in l or 'background' in l or 'color' in l)]
for r in found[:15]: print(r)
