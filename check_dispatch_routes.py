import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\modules\dispatch\routes.py", encoding='utf-8', errors='ignore').readlines()

hdr = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'app_header_actions' in l]
nav = [(i+1, l.rstrip()) for i,l in enumerate(lines) if '<nav class="bottom-nav">' in l]
gold = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'd4af37' in l]
hero = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'hero-title' in l or 'hero-sub' in l]

print("header_actions:", hdr)
print("bottom-nav:", nav)
print("金邊框:", gold[:3])
print("hero:", hero[:3])
