import sys
sys.stdout.reconfigure(encoding='utf-8')

files = [
    'engineering_app.py',
    'maintenance_app.py', 
    'sales_app.py',
    'employee_app.py',
    'router_mgmt_mobile.py',
]

for fname in files:
    fpath = rf"D:\shinnan ERP\app\routes\{fname}"
    lines = open(fpath, encoding='utf-8', errors='ignore').readlines()
    
    print(f"\n{'='*50}")
    print(f"{fname}")
    
    # 找 bottom-nav HTML
    nav_lines = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'bottom-nav' in l and ('<' in l or 'button' in l.lower())]
    print("bottom-nav buttons:")
    for r in nav_lines[:10]: print(f"  {r}")
    
    # 找 app_header_actions
    hdr = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'app_header_actions' in l]
    print("header_actions:", hdr)
