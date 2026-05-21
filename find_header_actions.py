lines = open(r"D:\shinnan ERP\app\routes\billing_app.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'app_header_actions' in l]
for r in found: print(r)
