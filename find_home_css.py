import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\home.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if '.hero' in l or '.logo' in l or '.brand' in l or 'font-size' in l]
for r in found[:30]: print(r)
