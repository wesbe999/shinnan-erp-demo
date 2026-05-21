import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\home.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'hero' in l.lower() and ('<' in l or 'font' in l or 'size' in l)]
for r in found[:15]: print(r)
