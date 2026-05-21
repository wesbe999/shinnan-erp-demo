import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\buildings_admin.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'openBuildingDetailModal' in l or 'buildingDetailModal' in l or ('building.ip' in l) or ('building.host' in l)]
for r in found[:15]: print(r)
