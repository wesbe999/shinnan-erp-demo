import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageFilter, ImageEnhance
import os

src = r"D:\shinnan ERP\app\static\home_globe_wire_transparent_stronger.png"
img = Image.open(src).convert("RGBA")

# 放大 2x
new_size = (img.width * 2, img.height * 2)
img_2x = img.resize(new_size, Image.LANCZOS)

# 分離 alpha 通道
r, g, b, a = img_2x.split()
rgb = Image.merge("RGB", (r, g, b))

# 銳化 RGB（不動 alpha）
rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.5, percent=180, threshold=2))

# 增強對比
rgb = ImageEnhance.Contrast(rgb).enhance(1.15)

# 合回 RGBA
r2, g2, b2 = rgb.split()
img_final = Image.merge("RGBA", (r2, g2, b2, a))

out = r"D:\shinnan ERP\app\static\home_globe_wire_transparent_stronger.png"
# 備份原檔
import shutil
shutil.copy(src, src.replace('.png', '_orig.png'))

img_final.save(out, "PNG", optimize=True)
print(f"完成！新尺寸: {img_final.size}")
print(f"新檔案大小: {os.path.getsize(out)//1024}KB")
