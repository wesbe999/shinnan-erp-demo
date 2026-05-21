import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
for f in glob.glob(r"D:\shinnan ERP\app\routes\*.py"):
    content = open(f, encoding='utf-8', errors='ignore').read()
    if '派工' in content and ('整理' in content or '新增' in content) and 'bottom-nav' in content:
        lines = content.splitlines()
        found = [(i+1, l) for i,l in enumerate(lines) if 'bottom-nav' in l and 'nav' in l.lower()]
        print(f.split('\\')[-1])
        for r in found[:3]: print(' ', r)
