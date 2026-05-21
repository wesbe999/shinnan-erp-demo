import re, sys
sys.stdout.reconfigure(encoding='utf-8')

GOLD_CSS = """.bottom-nav {
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
    .bottom-nav button.danger { background: #cf3b2f; border-color: #d4af37; color: #fff; }"""

pattern = re.compile(r'\.bottom-nav \{[^}]+\}(?:\s*\.bottom-nav[^\{]*\{[^}]+\})+', re.DOTALL)

for fname in ['engineering_app.py', 'maintenance_app.py', 'employee_app.py']:
    fpath = rf"D:\shinnan ERP\app\routes\{fname}"
    content = open(fpath, encoding='utf-8').read()
    matches = pattern.findall(content)
    if matches:
        new_content = pattern.sub(GOLD_CSS, content)
        open(fpath, 'w', encoding='utf-8').write(new_content)
        print(f"DONE: {fname} ({len(matches)} 區塊)")
    else:
        print(f"SKIP: {fname}")
