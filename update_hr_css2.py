import sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\hr_admin.py"
content = open(fpath, encoding='utf-8').read()

# 找舊的 dashboard-grid CSS 並替換
OLD_CSS = """    .dashboard-grid {{ display:grid; grid-template-columns:2fr 1fr; gap:20px; margin-top:20px; }}
    .dash-charts {{ display:flex; flex-direction:column; gap:16px; }}
    .dash-row2 {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
    .dash-side {{ display:flex; flex-direction:column; gap:0; }}"""

NEW_CSS = """    .dashboard-grid {{ display:flex; flex-direction:column; gap:20px; margin-top:20px; }}
    .dash-row {{ display:grid; gap:16px; }}
    .dash-row.col-3-1 {{ grid-template-columns:3fr 1fr; }}
    .dash-row.col-2-1-1 {{ grid-template-columns:2fr 1fr 1fr; }}
    .dash-row.col-1-1-1 {{ grid-template-columns:1fr 1fr 1fr; }}
    .dash-charts {{ display:flex; flex-direction:column; gap:16px; }}
    .dash-row2 {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
    .dash-side {{ display:flex; flex-direction:column; gap:0; }}"""

count = content.count(OLD_CSS)
print(f"CSS 找到: {count}")
content = content.replace(OLD_CSS, NEW_CSS, 1)
open(fpath, 'w', encoding='utf-8').write(content)
print("DONE")
