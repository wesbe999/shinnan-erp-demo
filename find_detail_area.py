import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\buildings_admin.py", encoding='utf-8', errors='ignore').readlines()
# 找詳細資料 modal 的區域欄位顯示
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if ('detail' in l.lower() or 'modal' in l.lower() or 'openDetail' in l or 'buildingDetail' in l)
         and ('area' in l.lower() or '區域' in l)]
for r in found[:15]: print(r)
