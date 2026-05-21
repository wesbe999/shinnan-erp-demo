import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
for f in glob.glob(r"D:\shinnan ERP\app\routes\*.py"):
    content = open(f, encoding='utf-8', errors='ignore').read()
    if '訊南工作管理系統' in content or '\u8a0a\u5357\u5de5\u4f5c\u7ba1\u7406\u7cfb\u7d71' in content:
        print(f.split('\\')[-1])
