import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\hr_admin.py", encoding='utf-8', errors='ignore').readlines()
# 找登出按鈕
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if '登出' in l and 'button' in l.lower()]
for r in found[:10]: print(r)
print(f"\n總行數: {len(lines)}")
