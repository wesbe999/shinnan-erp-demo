import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\billing.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if '登出' in l and 'button' in l.lower() and 'web-title' in ''.join(lines[max(0,i-5):i+5])]
for r in found[:10]: print(r)
