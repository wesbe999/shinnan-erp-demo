import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
for f in glob.glob(r"D:\shinnan ERP\app\routes\*.py"):
    content = open(f, encoding='utf-8', errors='ignore').read()
    if '\\u8a0a\\u5357\\u6d3e\\u5de5\\u7cfb\\u7d71' in content or '訊南派工系統' in content:
        print("找到:", f.split('\\')[-1])
    # 也找 unicode
    if '\u8a0a\u5357\u6d3e\u5de5\u7cfb\u7d71' in content:
        print("找到(unicode):", f.split('\\')[-1])
