import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\home.py", encoding='utf-8', errors='ignore').readlines()
# 找 canvas 或 img 或 background-image
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if 'canvas' in l.lower() or ('background' in l.lower() and ('url' in l.lower() or 'image' in l.lower()))
         or 'logo' in l.lower() or '.png' in l.lower() or '.jpg' in l.lower() or '.svg' in l.lower()]
for r in found[:20]: print(r)
