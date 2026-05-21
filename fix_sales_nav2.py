import re, sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\sales_app.py"
content = open(fpath, encoding='utf-8').read()

GOLD_CSS_4 = """.bottom-nav {
      position: fixed; left: 50%; bottom: 0; transform: translateX(-50%);
      width: 100%; max-width: 430px;
      display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 4px; padding: 8px 8px 12px;
      background: rgba(238,244,251,.96); border-top: 1px solid #d7e1ef;
      backdrop-filter: blur(10px); z-index: 20;
    }
    .bottom-nav button {
      height: 42px; min-width: 0; border: 2px solid #d4af37;
      border-radius: 12px; background: #fff; color: #102348;
      font-size: 12px; font-weight: 900; cursor: pointer;
    }
    .bottom-nav button.gold { background: transparent; border: 2px solid #d4af37; color: #d4af37; }
    .bottom-nav button.primary { background: #4f63e8; border-color: #d4af37; color: #fff; }
    .bottom-nav button.green { background: #16a34a; border-color: #d4af37; color: #fff; }
    .bottom-nav button.orange { background: #f97316; border-color: #d4af37; color: #fff; }
    .bottom-nav button.danger { background: #cf3b2f; border-color: #d4af37; color: #fff; }
    .bottom-nav button.dispatch-entry { background: #4f63e8; border-color: #d4af37; color: #fff; }
    .bottom-nav button.new-entry { background: #16a34a; border-color: #d4af37; color: #fff; }"""

pattern = re.compile(r'\.bottom-nav \{[^}]+\}(?:\s*\.bottom-nav[^\{]*\{[^}]+\})+', re.DOTALL)
new_content = pattern.sub(GOLD_CSS_4, content)
count = len(pattern.findall(content))
print(f"替換 {count} 個區塊")

open(fpath, 'w', encoding='utf-8').write(new_content)
print("DONE")
