import re, sys
sys.stdout.reconfigure(encoding='utf-8')

# 統一的金邊框 CSS 樣式
GOLD_CSS = """
    .bottom-nav {
      position: fixed;
      left: 50%;
      bottom: 0;
      transform: translateX(-50%);
      width: 100%;
      max-width: 430px;
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 4px;
      padding: 8px 8px 12px;
      background: rgba(238,244,251,.96);
      border-top: 1px solid #d7e1ef;
      backdrop-filter: blur(10px);
      z-index: 20;
    }
    .bottom-nav button {
      height: 42px;
      min-width: 0;
      border: 2px solid #d4af37;
      border-radius: 12px;
      background: #fff;
      color: #102348;
      font-size: 11px;
      font-weight: 1000;
      line-height: 1.1;
      padding: 0 2px;
      cursor: pointer;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .bottom-nav button.gold {
      background: transparent;
      border: 2px solid #d4af37;
      color: #d4af37;
    }
    .bottom-nav button.primary {
      background: #4f63e8;
      border-color: #d4af37;
      color: #fff;
    }
    .bottom-nav button.green {
      background: #16a34a;
      border-color: #d4af37;
      color: #fff;
    }
    .bottom-nav button.orange {
      background: #f97316;
      border-color: #d4af37;
      color: #fff;
    }
    .bottom-nav button.danger {
      background: #cf3b2f;
      border-color: #d4af37;
      color: #fff;
    }"""

# 統一的首頁+登出按鈕 HTML
HOME_BTN = '<button type="button" class="gold" onclick="window.location.href=\'/app\'">🏠 首頁</button>'
LOGOUT_BTN = '<button type="button" class="danger" onclick="window.location.href=\'/employee/logout?next=/employee/login\'">登出</button>'

# 各 APP 的底部按鈕（中間按鈕保留原有的）
APP_NAV = {
    'engineering_app.py': [
        HOME_BTN,
        '<button type="button" class="primary" id="nav_schedule_btn">📅 排班</button>',
        '<button type="button" class="green" onclick="window.location.href=\'/app/engineering/schedule\'">📋 工程表</button>',
        LOGOUT_BTN,
    ],
    'maintenance_app.py': [
        HOME_BTN,
        '<button type="button" class="primary" onclick="loadTickets()">🔄 重整</button>',
        '<button type="button" class="orange" onclick="showCreateTicket && showCreateTicket()">➕ 新增</button>',
        LOGOUT_BTN,
    ],
    'sales_app.py': [
        HOME_BTN,
        '<button type="button" class="orange" onclick="window.location.href=\'/app/sales/new\'">➕ 新增</button>',
        '<button type="button" class="primary" onclick="loadData && loadData()">🔄 重整</button>',
        LOGOUT_BTN,
    ],
    'router_mgmt_mobile.py': [
        HOME_BTN,
        '<button type="button" class="primary" onclick="selectArea(\'__ALL__\')">📡 全部</button>',
        '<button type="button" class="green" onclick="startPing && startPing()">🔄 Ping</button>',
        LOGOUT_BTN,
    ],
}

for fname, btns in APP_NAV.items():
    fpath = rf"D:\shinnan ERP\app\routes\{fname}"
    content = open(fpath, encoding='utf-8').read()
    original = content
    
    # 1. 移除 app_header_actions.js
    content = re.sub(r'\s*<script src="/static/app_header_actions\.js[^"]*"></script>', '', content)
    
    # 2. 替換 bottom-nav CSS（找到舊的 .bottom-nav { ... } 區塊替換）
    # 找到 .bottom-nav 開始到最後一個 .bottom-nav 相關的 } 
    css_pattern = r'(\.bottom-nav\s*\{[^}]+\}(?:\s*\.bottom-nav[^\{]+\{[^}]+\})*)'
    if re.search(css_pattern, content):
        # 把所有 bottom-nav CSS 替換成統一版本
        content = re.sub(css_pattern, GOLD_CSS.strip(), content, count=1)
    else:
        # 沒有 bottom-nav CSS，在 </style> 前加入
        content = content.replace('</style>', GOLD_CSS + '\n    </style>', 1)
    
    # 3. 替換或加入 bottom-nav HTML
    nav_html = '\n    <nav class="bottom-nav">\n      ' + '\n      '.join(btns) + '\n    </nav>'
    
    if '<nav class="bottom-nav">' in content:
        # 替換現有的 bottom-nav
        content = re.sub(r'<nav class="bottom-nav">.*?</nav>', nav_html.strip(), content, flags=re.DOTALL)
    else:
        # 在 </div> 或 </body> 前加入
        content = content.replace('</body>', nav_html + '\n</body>', 1)
    
    if content != original:
        open(fpath, 'w', encoding='utf-8').write(content)
        print(f"DONE: {fname}")
    else:
        print(f"SKIP: {fname} (no change)")
