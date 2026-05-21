import sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\billing_app.py"
content = open(fpath, encoding='utf-8').read()

# 替換 building_name 的 COALESCE 邏輯
# 舊：COALESCE(b.name, c.building_name, c.building_no, '未命名大樓')
# 新：COALESCE(c.building_name, '未命名大樓')

OLD1 = "COALESCE({b_name_expr}, {c_building_name}, {c_building_no}, '未命名大樓') AS building_name,"
NEW1 = "COALESCE({c_building_name}, '未命名大樓') AS building_name,"

OLD2 = "COALESCE({b_name_expr_for_overdue}, {c_building_name_for_overdue}, {c_building_no_for_overdue}, '未命名大樓') AS building_name,"
NEW2 = "COALESCE({c_building_name_for_overdue}, '未命名大樓') AS building_name,"

c1 = content.count(OLD1)
c2 = content.count(OLD2)
print(f"找到 OLD1: {c1}, OLD2: {c2}")

content = content.replace(OLD1, NEW1)
content = content.replace(OLD2, NEW2)

open(fpath, 'w', encoding='utf-8').write(content)
print("DONE")
