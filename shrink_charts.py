import sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\hr_admin.py"
lines = open(fpath, encoding='utf-8').readlines()

# 找 canvas height 並縮小
changes = 0
for i, l in enumerate(lines):
    if 'canvas id=' in l and 'height=' in l:
        old = l
        # deptChart 80 -> 60, 其他 200 -> 120
        if 'deptChart' in l:
            lines[i] = l.replace('height="80"', 'height="60"')
        else:
            lines[i] = l.replace('height="200"', 'height="120"')
        if lines[i] != old:
            changes += 1
            print(f"  行{i+1}: {lines[i].strip()}")

open(fpath, 'w', encoding='utf-8').writelines(lines)
print(f"共修改 {changes} 處")
