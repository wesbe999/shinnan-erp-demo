import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
for f in glob.glob(r"D:\shinnan ERP\app\routes\*.py"):
    content = open(f, encoding='utf-8', errors='ignore').read()
    if '訊南工作管理系統' in content:
        lines = content.splitlines()
        found = [(i+1, l) for i,l in enumerate(lines) if '訊南工作管理系統' in l or 'router.get' in l.lower() and '"/app"' in l]
        print(f.split('\\')[-1])
        for r in found[:5]: print(' ', r)
