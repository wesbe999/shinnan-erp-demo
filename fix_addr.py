content = open(r"D:\shinnan ERP\app\routes\billing_app.py", encoding='utf-8').read()

OLD = 'c_address = "c.install_address" if "install_address" in customer_cols else ("c.service_address" if "service_address" in customer_cols else "\'\'")'
NEW = 'c_address = "COALESCE(c.room_no, c.floor_text)" if "room_no" in customer_cols else ("c.install_address" if "install_address" in customer_cols else ("c.service_address" if "service_address" in customer_cols else "\'\'"))'

count = content.count(OLD)
print(f"找到 {count} 處")
content = content.replace(OLD, NEW)
open(r"D:\shinnan ERP\app\routes\billing_app.py", 'w', encoding='utf-8').write(content)
print("完成!")
