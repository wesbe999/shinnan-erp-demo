import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import os

src = r"D:\shinnan ERP\app\static\home_globe_wire_transparent_stronger.png"
img = Image.open(src)
print(f"原始尺寸: {img.size}, 模式: {img.mode}")
print(f"檔案大小: {os.path.getsize(src)//1024}KB")
