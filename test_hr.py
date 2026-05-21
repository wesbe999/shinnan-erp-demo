import sys, traceback
sys.path.insert(0, r"D:\shinnan ERP")
sys.stdout.reconfigure(encoding='utf-8')
try:
    from app.routes.hr_admin import hr_home_page
    print("import OK")
except Exception as e:
    traceback.print_exc()
