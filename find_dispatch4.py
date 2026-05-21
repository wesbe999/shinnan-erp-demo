import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
for f in glob.glob(r"D:\shinnan ERP\app\routes\*.py"):
    content = open(f, encoding='utf-8', errors='ignore').read()
    if 'dispatch' in content.lower() and 'hero-title' in content:
        lines = content.splitlines()
        found = [(i+1, l) for i,l in enumerate(lines) if 'hero-title' in l]
        print(f.split('\\')[-1])
        for r in found[:3]: print(' ', r)
