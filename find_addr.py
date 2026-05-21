lines = open(r"D:\shinnan ERP\app\routes\billing_app.py", encoding='utf-8', errors='ignore').readlines()
# 找地址顯示的部分
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) if 'install_address' in l or 'service_address' in l or 'address' in l.lower() and ('floor' in l.lower() or 'room' in l.lower() or 'building_name' in l.lower())]
for r in found[:20]: print(r)
