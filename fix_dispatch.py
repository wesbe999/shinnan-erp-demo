import re, sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\admin_dispatch.py"
content = open(fpath, encoding='utf-8').read()

# 1. 移除 app_header_actions.js
content = re.sub(r'\s*<script src="/static/app_header_actions\.js[^"]*"></script>', '', content)

# 2. 移除整個 installHeaderActions JS 區塊（從 style id="cl15i10_dispatch..." 到對應結尾）
content = re.sub(
    r'<style id="cl15i10_dispatch_actions_to_header_right_v1">.*?</style>',
    '', content, flags=re.DOTALL
)
content = re.sub(
    r'<script>\s*\(function\(\)\s*\{.*?installHeaderActions.*?\}\)\(\);\s*</script>',
    '', content, flags=re.DOTALL
)

# 3. 在 </head> 前加公版 CSS
HERO_LINK = '<link rel="stylesheet" href="/static/app_header_unified.css?v=20260511_title_v1">'
if HERO_LINK not in content:
    content = content.replace('</head>', f'{HERO_LINK}\n</head>', 1)

# 4. 在 <body> 後、第一個內容前加公版 hero
HERO_HTML = '''<section class="hero app-standard-hero">
  <div class="hero-main">
    <span class="hero-logo"><img class="hero-logo-img" src="/static/shinnan_home_logo.png" alt="Logo"></span>
    <h1 class="hero-title">訊南派工系統</h1>
  </div>
  <div class="hero-sub">__DISPATCH_USER__</div>
</section>'''

if 'hero app-standard-hero' not in content:
    content = content.replace('<body>', f'<body>\n{HERO_HTML}', 1)

# 5. 加底部 nav + CSS
BOTTOM_NAV = '''
<style>
.bottom-nav{position:fixed;left:50%;bottom:0;transform:translateX(-50%);width:100%;max-width:520px;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:4px;padding:8px 8px 12px;background:rgba(238,244,251,.96);border-top:1px solid #d7e1ef;backdrop-filter:blur(10px);z-index:200;}
.bottom-nav button{height:42px;min-width:0;border:2px solid #d4af37;border-radius:12px;background:#fff;color:#102348;font-size:12px;font-weight:900;cursor:pointer;}
.bottom-nav button.gold{background:transparent;border:2px solid #d4af37;color:#d4af37;}
.bottom-nav button.primary{background:#4f63e8;border-color:#d4af37;color:#fff;}
.bottom-nav button.green{background:#16a34a;border-color:#d4af37;color:#fff;}
.bottom-nav button.danger{background:#cf3b2f;border-color:#d4af37;color:#fff;}
body{padding-bottom:70px;}
</style>
<nav class="bottom-nav">
  <button type="button" class="gold" onclick="window.location.href='/app'">🏠 首頁</button>
  <button type="button" class="primary" onclick="loadAll()">🔄 重整</button>
  <button type="button" class="green" onclick="openCreateModal()">➕ 新增</button>
  <button type="button" class="danger" onclick="logout()">登出</button>
</nav>'''

if 'bottom-nav' not in content:
    content = content.replace('</body>', f'{BOTTOM_NAV}\n</body>', 1)

# 6. 替換 __DISPATCH_USER__ 
# 找 user_line 的變數名
lines = content.splitlines()
user_vars = [(i, l) for i,l in enumerate(lines) if 'user_line' in l or 'display_name' in l.lower() and 'replace' in l]
print("user var:", user_vars[:3])

open(fpath, 'w', encoding='utf-8').write(content)
print("DONE")
