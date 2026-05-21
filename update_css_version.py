import sys
sys.stdout.reconfigure(encoding='utf-8')

# 更新 billing_app 的 CSS 版本號
fpath = r"D:\shinnan ERP\app\routes\billing_app.py"
content = open(fpath, encoding='utf-8').read()
content = content.replace(
    'app_header_unified.css?v=20260511_title_v1',
    'app_header_unified.css?v=20260520_unified'
)
open(fpath, 'w', encoding='utf-8').write(content)
print("billing_app.py 版本號更新")

# 其他 APP 也更新
import glob
for fname in glob.glob(r"D:\shinnan ERP\app\routes\*.py"):
    c = open(fname, encoding='utf-8').read()
    if 'app_header_unified.css' in c:
        new_c = c.replace(
            'app_header_unified.css?v=20260511_title_v1',
            'app_header_unified.css?v=20260520_unified'
        )
        if new_c != c:
            open(fname, 'w', encoding='utf-8').write(new_c)
            print(f"更新: {fname.split(chr(92))[-1]}")
