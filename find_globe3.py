import sys, os
sys.stdout.reconfigure(encoding='utf-8')
lines = open(r"D:\shinnan ERP\app\routes\home.py", encoding='utf-8', errors='ignore').readlines()
found = [(i+1, l.rstrip()) for i,l in enumerate(lines) 
         if 'url(' in l.lower() or 'background' in l.lower() and ('image' in l.lower() or 'url' in l.lower())]
for r in found[:15]: print(r)

# 看靜態資源
static = r"D:\shinnan ERP\app\static"
imgs = [f for f in os.listdir(static) if f.lower().endswith(('.png','.jpg','.webp')) and ('globe' in f.lower() or 'earth' in f.lower() or 'bg' in f.lower() or 'home' in f.lower() or 'world' in f.lower())]
print("\n靜態圖片:")
for f in imgs:
    size = os.path.getsize(os.path.join(static, f))
    print(f"  {f} ({size//1024}KB)")
