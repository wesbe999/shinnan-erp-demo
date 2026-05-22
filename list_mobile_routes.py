import os, glob, sys
sys.stdout.reconfigure(encoding='utf-8')

for f in glob.glob(r"D:\shinnan ERP\app\routes\*.py"):
    lines = open(f, encoding='utf-8', errors='ignore').readlines()
    routes = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'router.get' in l.lower() and ('app/' in l or 'mobile' in l.lower() or 'billing' in l.lower())]
    if routes:
        print(f"\n=== {f.split(chr(92))[-1]} ===")
        for r in routes[:10]: print(r)
