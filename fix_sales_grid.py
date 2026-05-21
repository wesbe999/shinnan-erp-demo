import re, sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\sales_app.py"
content = open(fpath, encoding='utf-8').read()

# 改 grid 5欄
content = content.replace(
    'grid-template-columns: repeat(4, minmax(0, 1fr));',
    'grid-template-columns: repeat(5, minmax(0, 1fr));'
)
open(fpath, 'w', encoding='utf-8').write(content)
print("DONE")
