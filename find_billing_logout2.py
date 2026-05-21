import sys, os, glob
sys.stdout.reconfigure(encoding='utf-8')

# 找所有含 cl15i10 的檔案
for f in glob.glob(r"D:\shinnan ERP\app\routes\billing.py"):
    lines = open(f, encoding='utf-8', errors='ignore').readlines()
    found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'cl15i10' in l or ('返回首頁' in l and 'button' in l.lower())]
    if found:
        print(f"\n{f.split(chr(92))[-1]}:")
        for r in found[:10]: print(r)

# 找 static JS
for f in glob.glob(r"D:\shinnan ERP\app\static\*.js"):
    content = open(f, encoding='utf-8', errors='ignore').read()
    if 'cl15i10' in content or ('返回首頁' in content and '登出' in content):
        print(f"\n{f.split(chr(92))[-1]}: 找到相關內容")
        lines = content.splitlines()
        found = [(i+1, l) for i,l in enumerate(lines) if '登出' in l or 'logout' in l.lower() and 'color' in l.lower()]
        for r in found[:5]: print(r)
