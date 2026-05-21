import sys, re
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\hr_admin.py"
content = open(fpath, encoding='utf-8').read()

# 找第一個 dashboard-grid 的 CSS 區塊（有單括號的那個），替換成雙括號版本
OLD = """
    .dashboard-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-top: 20px;
    }
    .dash-panel {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,.07);
      border: 1px solid #e5e7eb;
    }
    .dash-panel-title {
      font-size: 15px;
      font-weight: 800;
      color: #1e3a5f;
      margin-bottom: 14px;
      padding-bottom: 10px;
      border-bottom: 2px solid #eef3f9;
    }
    .dash-list { list-style: none; padding: 0; margin: 0; }
    .dash-list li { padding: 8px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px; }
    .dash-list li:last-child { border-bottom: none; }
    .dash-list a { color: #1d4ed8; text-decoration: none; }
    .dash-list a:hover { text-decoration: underline; }
    .dash-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .dash-table tr { border-bottom: 1px solid #f1f5f9; }
    .dash-table td { padding: 8px 4px; color: #475569; }
    .dash-table td.val { font-weight: 800; color: #1e3a5f; text-align: right; }
    .dash-shortcuts { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .shortcut-btn {
      display: block; text-align: center; padding: 12px 8px;
      background: #eef3f9; border-radius: 8px; font-size: 13px;
      font-weight: 700; color: #1e3a5f; text-decoration: none;
      border: 1px solid #d7e1ef; transition: .15s;
    }
    .shortcut-btn:hover { background: #1d4ed8; color: #fff; border-color: #1d4ed8; }"""

NEW = """
    .dashboard-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:20px; }}
    .dash-panel {{ background:#fff; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,.07); border:1px solid #e5e7eb; }}
    .dash-panel-title {{ font-size:15px; font-weight:800; color:#1e3a5f; margin-bottom:14px; padding-bottom:10px; border-bottom:2px solid #eef3f9; }}
    .dash-list {{ list-style:none; padding:0; margin:0; }}
    .dash-list li {{ padding:8px 0; border-bottom:1px solid #f1f5f9; font-size:13px; }}
    .dash-list li:last-child {{ border-bottom:none; }}
    .dash-list a {{ color:#1d4ed8; text-decoration:none; }}
    .dash-list a:hover {{ text-decoration:underline; }}
    .dash-table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    .dash-table tr {{ border-bottom:1px solid #f1f5f9; }}
    .dash-table td {{ padding:8px 4px; color:#475569; }}
    .dash-table td.val {{ font-weight:800; color:#1e3a5f; text-align:right; }}
    .dash-shortcuts {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
    .shortcut-btn {{ display:block; text-align:center; padding:12px 8px; background:#eef3f9; border-radius:8px; font-size:13px; font-weight:700; color:#1e3a5f; text-decoration:none; border:1px solid #d7e1ef; }}
    .shortcut-btn:hover {{ background:#1d4ed8; color:#fff; border-color:#1d4ed8; }}"""

count = content.count(OLD)
print(f"找到 {count} 處")
content = content.replace(OLD, NEW, 1)
open(fpath, 'w', encoding='utf-8').write(content)
print("DONE")
