import re, sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\employee_app.py"
content = open(fpath, encoding='utf-8').read()

# 找壓縮的 bottom-nav CSS
pattern = re.compile(r'\.bottom-nav button\{[^}]+\}(?:\s*\.bottom-nav button\.[^\{]+\{[^}]+\})*')
matches = pattern.findall(content)
print(f"找到 {len(matches)} 個")
if matches:
    print("第一個:", matches[0][:100])

GOLD = """.bottom-nav button{height:54px;border:2px solid #d4af37;border-radius:18px;background:#fff;color:#102348;font-size:16px;font-weight:1000;cursor:pointer}
.bottom-nav button.gold{background:transparent;border:2px solid #d4af37;color:#d4af37}
.bottom-nav button.primary{background:#365ee8;border-color:#d4af37;color:#fff}
.bottom-nav button.danger{background:#cf3b2f;border-color:#d4af37;color:#fff}"""

new_content = pattern.sub(GOLD, content)
open(fpath, 'w', encoding='utf-8').write(new_content)
print("DONE")
