import sys
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\engineering_app.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if '<nav class="bottom-nav">' in l or ('button' in l and 'onclick' in l and 'bottom' in ''.join(lines[max(0,i-5):i+5]).lower())]
for r in found[:30]: print(r)
