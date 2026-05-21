import re, sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\admin_dispatch.py"
content = open(fpath, encoding='utf-8').read()

# 查 bottom-nav 和 header_actions
lines = content.splitlines()
nav = [(i+1, l) for i,l in enumerate(lines) if 'bottom-nav' in l and ('<nav' in l or 'button' in l)]
hdr = [(i+1, l) for i,l in enumerate(lines) if 'app_header_actions' in l]
hero = [(i+1, l) for i,l in enumerate(lines) if 'hero-title' in l]

print("bottom-nav:", nav[:5])
print("header_actions:", hdr)
print("hero-title:", hero[:3])
