import sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\hr_admin.py"
lines = open(fpath, encoding='utf-8').readlines()

# 替換第 409 行
lines[408] = '.dashboard-grid {{ display:flex; flex-direction:column; gap:20px; margin-top:20px; }}\n'
lines[409] = '    .dash-row {{ display:grid; gap:16px; }}\n'
lines[410] = '    .dash-row.col-3-1 {{ grid-template-columns:3fr 1fr; }}\n'
lines[411] = '    .dash-row.col-1-1 {{ grid-template-columns:1fr 1fr; }}\n'

open(fpath, 'w', encoding='utf-8').writelines(lines)
print("DONE")
