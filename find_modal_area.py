import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\buildings_admin.py", encoding='utf-8', errors='ignore').readlines()
# 找 modal area 顯示相關
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if 'detail_area' in l or 'modal_area' in l or ('area' in l and ('innerText' in l or 'textContent' in l or 'innerHTML' in l))]
for r in found[:15]: print(r)
