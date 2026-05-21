import re, sys
sys.stdout.reconfigure(encoding='utf-8')

files = [
    'engineering_app.py',
    'sales_app.py',
    'employee_app.py',
    'router_mgmt_mobile.py',
]

NAV_PATTERN = re.compile(
    r'\n    <nav class="bottom-nav">.*?</nav>\n</body>"',
    re.DOTALL
)

for fname in files:
    fpath = rf"D:\shinnan ERP\app\routes\{fname}"
    content = open(fpath, encoding='utf-8').read()
    
    # 找到被插進字串裡的 nav
    if NAV_PATTERN.search(content):
        # 移除被插入的 nav，並修復 </body>"
        content = NAV_PATTERN.sub('</body>"', content)
        open(fpath, 'w', encoding='utf-8').write(content)
        print(f"FIXED: {fname}")
    else:
        print(f"OK: {fname}")
