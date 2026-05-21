import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\hr_admin.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'col-1-1-1' in l or 'col-1-1' in l or 'dash-row' in l]
for r in found[:10]: print(r)
