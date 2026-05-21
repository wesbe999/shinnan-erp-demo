import sys, os
sys.stdout.reconfigure(encoding='utf-8')
dispatch_dir = r"D:\shinnan ERP\app\modules\dispatch"
for f in os.listdir(dispatch_dir):
    print(f)
