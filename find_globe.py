import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\home.py", encoding='utf-8', errors='ignore').readlines()
# 找地球/canvas/svg 相關
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if 'canvas' in l.lower() or 'globe' in l.lower() or 'sphere' in l.lower() 
         or 'earth' in l.lower() or 'three' in l.lower() or 'webgl' in l.lower()
         or 'network' in l.lower() or '地球' in l or 'mesh' in l.lower()]
for r in found[:15]: print(r)
