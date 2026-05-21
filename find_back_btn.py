import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
# 搜尋所有包含 返回首頁 按鈕 AND 整理 AND 新增 的檔案
for f in glob.glob(r"D:\shinnan ERP\app\routes\*.py"):
    content = open(f, encoding='utf-8', errors='ignore').read()
    if '返回首頁' in content and '整理' in content and '新增' in content:
        print(f.split('\\')[-1])
        lines = content.splitlines()
        found = [(i+1, l) for i,l in enumerate(lines) if '返回首頁' in l]
        for r in found[:3]: print(' ', r)
