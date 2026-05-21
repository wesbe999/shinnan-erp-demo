import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\billing_app.py", encoding='utf-8', errors='ignore').readlines()

# 找 building_name 的 SQL 查詢
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if 'building_name' in l and ('SELECT' in l or 'COALESCE' in l or 'JOIN' in l or 'b_name' in l or 'b.name' in l)]
for r in found[:15]: print(r)
