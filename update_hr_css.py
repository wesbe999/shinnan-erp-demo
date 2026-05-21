import sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\hr_admin.py"
content = open(fpath, encoding='utf-8').read()

ADD_CSS = """
    .dashboard-grid {{ display:grid; grid-template-columns:2fr 1fr; gap:20px; margin-top:20px; }}
    .dash-charts {{ display:flex; flex-direction:column; gap:16px; }}
    .dash-row2 {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
    .dash-side {{ display:flex; flex-direction:column; gap:0; }}"""

# 找 .dashboard-grid 的雙括號版本並替換
OLD = "    .dashboard-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:20px; }}"
NEW = ADD_CSS.strip()

count = content.count(OLD)
print(f"找到 {count} 處")
content = content.replace(OLD, NEW, 1)
open(fpath, 'w', encoding='utf-8').write(content)
print("DONE")
