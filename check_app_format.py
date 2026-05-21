import glob, sys
sys.stdout.reconfigure(encoding='utf-8')

files = {
    'billing_app.py': '/app/billing',
    'engineering_app.py': '/app/engineering',
    'maintenance_app.py': '/app/maintenance',
    'sales_app.py': '/app/sales',
    'employee_app.py': '/app/employee/leave',
    'router_mgmt_mobile.py': '/router-mgmt-mobile',
}

for fname, route in files.items():
    fpath = rf"D:\shinnan ERP\app\routes\{fname}"
    lines = open(fpath, encoding='utf-8', errors='ignore').readlines()
    
    has_header_actions = any('app_header_actions' in l for l in lines)
    has_bottom_nav = any('bottom-nav' in l for l in lines)
    has_gold_border = any('d4af37' in l for l in lines)
    logout_in_bottom = any('logout' in l and 'bottom' in ''.join(lines[max(0,i-5):i+5]).lower() for i,l in enumerate(lines) if 'logout' in l)
    home_in_bottom = any(('/app' in l or '首頁' in l) and 'bottom' in ''.join(lines[max(0,i-5):i+5]).lower() for i,l in enumerate(lines) if '/app' in l or '首頁' in l)
    
    print(f"\n{fname} ({route})")
    print(f"  header_actions.js: {'有' if has_header_actions else '無'}")
    print(f"  bottom-nav: {'有' if has_bottom_nav else '無'}")
    print(f"  金邊框(d4af37): {'有' if has_gold_border else '無'}")
