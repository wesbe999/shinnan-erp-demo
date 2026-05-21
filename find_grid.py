import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\static\web_title_unified.css", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'grid-template' in l or ('web-title-main' in l and '{' in l)]
for r in found[:10]: print(r)
