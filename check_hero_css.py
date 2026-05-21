import sys, glob
sys.stdout.reconfigure(encoding='utf-8')

files = [
    'billing_app.py',
    'engineering_app.py', 
    'maintenance_app.py',
    'sales_app.py',
    'employee_app.py',
    'router_mgmt_mobile.py',
]

for fname in files:
    fpath = rf"D:\shinnan ERP\app\routes\{fname}"
    lines = open(fpath, encoding='utf-8', errors='ignore').readlines()
    found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
             if 'hero-title' in l or 'hero-sub' in l or 'hero-logo' in l]
    if found:
        print(f"\n{fname}:")
        for r in found[:8]: print(f"  {r}")
