import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\admin_dispatch.py", encoding='utf-8', errors='ignore').readlines()

hero = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'hero app-standard-hero' in l or 'bottom-nav' in l or '__DISPATCH_USER__' in l]
link = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'app_header_unified' in l]
print("hero/nav:", hero[:5])
print("header_unified:", link[:3])
