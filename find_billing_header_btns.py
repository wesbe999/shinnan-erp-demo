import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\billing.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if '建立資料' in l or '開立發票' in l or '客戶清單' in l]
for r in found[:10]: print(r)
