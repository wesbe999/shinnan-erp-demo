import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\employee_app.py", encoding='utf-8', errors='ignore').readlines()

# 找所有 bottom-nav HTML
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if '<nav class="bottom-nav">' in l]
print("bottom-nav 位置:", found)

# 找 app_header_actions 殘留
hdr = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'app_header_actions' in l]
print("header_actions:", hdr)

# 找返回首頁/登出在 hero 區域
back = [(i+1, l.rstrip()) for i,l in enumerate(lines) if ('返回首頁' in l or '登出' in l) and 'button' in l.lower()]
print("hero 裡的按鈕:", back[:10])
