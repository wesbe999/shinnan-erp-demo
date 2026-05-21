import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
# 找所有包含 app_header_actions 的 py 檔案
for f in glob.glob(r"D:\shinnan ERP\app\routes\*.py"):
    content = open(f, encoding='utf-8', errors='ignore').read()
    if 'app_header_actions' in content:
        print(f.split('\\')[-1])
