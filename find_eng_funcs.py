import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\engineering_app.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'function ' in l and ('ticket' in l.lower() or 'modal' in l.lower() or 'sheet' in l.lower() or 'create' in l.lower() or 'open' in l.lower())]
for r in found[:20]: print(r)
