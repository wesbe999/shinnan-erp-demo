import re, sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\employee_app.py"
content = open(fpath, encoding='utf-8').read()

# 移除所有 app_header_actions.js
before = content.count('app_header_actions')
content = re.sub(r'\s*<script src="/static/app_header_actions\.js[^"]*"></script>', '', content)
after = content.count('app_header_actions')
print(f"移除 app_header_actions: {before} -> {after}")

# 加金邊框到所有 bottom-nav button
GOLD_BTN_CSS = """
.bottom-nav button{height:54px;border:2px solid #d4af37;border-radius:18px;background:#fff;color:#102348;font-size:16px;font-weight:1000}
.bottom-nav button.primary{background:#365ee8;border-color:#d4af37;color:#fff}
.bottom-nav button.gold{background:transparent;border:2px solid #d4af37;color:#d4af37}
.bottom-nav button.danger{background:#cf3b2f;border-color:#d4af37;color:#fff}"""

# 替換舊的 bottom-nav button CSS
content = re.sub(
    r'\.bottom-nav button\{[^}]+\}\s*\.bottom-nav button\.primary\{[^}]+\}',
    GOLD_BTN_CSS.strip(),
    content
)

# 找到所有 bottom-nav，加入首頁和登出按鈕
HOME_BTN = '<button type="button" class="gold" onclick="window.location.href=\'/app\'">🏠 首頁</button>'
LOGOUT_BTN = '<button type="button" class="danger" onclick="window.location.href=\'/employee/logout?next=/employee/login\'">登出</button>'

def add_home_logout(match):
    nav_content = match.group(0)
    if '首頁' not in nav_content and 'logout' not in nav_content:
        nav_content = nav_content.replace('<nav class="bottom-nav">', 
            f'<nav class="bottom-nav">\n      {HOME_BTN}')
        nav_content = nav_content.replace('</nav>', 
            f'  {LOGOUT_BTN}\n    </nav>')
    return nav_content

content = re.sub(r'<nav class="bottom-nav">.*?</nav>', add_home_logout, content, flags=re.DOTALL)

open(fpath, 'w', encoding='utf-8').write(content)
print("DONE: employee_app.py")
