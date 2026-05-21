import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
for f in glob.glob(r"D:\shinnan ERP\app\routes\*.py"):
    lines = open(f, encoding='utf-8', errors='ignore').readlines()
    if any('訊南派工系統' in l or 'app/dispatch' in l for l in lines):
        found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'app/dispatch' in l and 'router.get' in l.lower()]
        if found:
            print(f.split('\\')[-1])
            for r in found[:5]: print(' ', r)
