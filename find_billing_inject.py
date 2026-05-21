import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\billing.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if ('返回首頁' in l or '建立資料' in l) and ('appendChild' in l or 'innerHTML' in l or 'cloneButton' in l or 'createElement' in l)]
for r in found[:10]: print(r)
