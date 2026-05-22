import sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\hr_admin.py"
content = open(fpath, encoding='utf-8').read()

OLD = "    .dash-panel {{ background:#fff; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,.07); border:1px solid #e5e7eb; }}"
NEW = """    .dash-panel {{ background:#fff; border-radius:12px; padding:14px 16px; box-shadow:0 2px 8px rgba(0,0,0,.07); border:1px solid #e5e7eb; }}
    .dash-panel canvas {{ max-height:160px; }}
    .dash-panel-title {{ font-size:13px; }}"""

count = content.count(OLD)
print(f"找到: {count}")
content = content.replace(OLD, NEW, 1)
open(fpath, 'w', encoding='utf-8').write(content)
print("DONE")
