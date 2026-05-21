lines = open(r"D:\shinnan ERP\app\routes\billing_app.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'onclick' in l and ('應發' in l or '逾期' in l or 'overdue' in l.lower() or 'summary' in l.lower())]
for r in found[:15]: print(r)
