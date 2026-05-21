import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\buildings_admin.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'web-title-user' in l and ('{' in l or 'position' in l or 'right' in l or 'left' in l or 'top' in l or 'bottom' in l)]
for r in found[:15]: print(r)
