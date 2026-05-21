import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\engineering_app.py", encoding='utf-8', errors='ignore').readlines()
# 找所有按鈕
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'button' in l.lower() and 'onclick' in l and '<button' in l and 'modal' not in l.lower() and 'close' not in l.lower() and 'cancel' not in l.lower()]
for r in found[:20]: print(r)
