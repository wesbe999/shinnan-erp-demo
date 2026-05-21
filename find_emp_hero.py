import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\employee_app.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'hero' in l and ('<section' in l or 'hero-title' in l or 'hero-logo' in l or 'app-standard' in l)]
for r in found[:10]: print(r)
