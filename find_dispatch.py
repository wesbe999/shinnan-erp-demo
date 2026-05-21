import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
for f in glob.glob(r"D:\shinnan ERP\app\routes\*.py"):
    lines = open(f, encoding='utf-8', errors='ignore').readlines()
    found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if '派工系統' in l or 'dispatch' in l.lower() and 'app' in l.lower() and 'router.get' in l.lower()]
    if found:
        print(f.split('\\')[-1])
        for r in found[:3]: print(' ', r)
