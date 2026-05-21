import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\billing.py", encoding='utf-8', errors='ignore').readlines()
# 找 cl15i10 style 的注入
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if 'cl15i10' in l or 'installHeader' in l or 'cloneButton' in l]
for r in found[:15]: print(r)
