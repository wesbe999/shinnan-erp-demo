import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\billing.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'web-title-main' in l or 'web-title-actions' in l or 'web-title-system' in l]
for r in found[:10]: print(r)
