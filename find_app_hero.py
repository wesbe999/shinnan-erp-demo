import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\employee_app.py", encoding='utf-8', errors='ignore').readlines()
# 找 /app 頁面的 hero
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if i >= 3033 and ('hero' in l.lower() or 'logo' in l.lower()) and i < 3300]
for r in found[:10]: print(r)
