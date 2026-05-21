lines = open(r"D:\shinnan ERP\app\routes\billing_app.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'summary-card' in l or ('應發' in l and 'card' in l.lower())]
for r in found[:15]: print(r)
