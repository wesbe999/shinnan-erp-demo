lines = open(r"D:\shinnan ERP\app\routes\billing_app.py", encoding='utf-8', errors='ignore').readlines()
# 找 hero/header 和 bottom-nav
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'hero' in l.lower() or 'bottom-nav' in l.lower() or '返回首頁' in l or '登出' in l or 'bottom_nav' in l.lower()]
for r in found[:20]: print(r)
