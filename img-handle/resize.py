from PIL import Image
Image.MAX_IMAGE_PIXELS = None  # 这将移除像素数量的限制

# 1. 打开图片
image = Image.open(r'e:\work\苏大-鹌鹑蛋好吃\热力图\contact_transparent_01_L.png').convert('L')  # 确保图像是灰度模式

# 2. 获取图片的原始尺寸
original_width, original_height = image.size

# 3. 计算新的宽度，保持宽高比不变
new_height = 1000
new_width = int((new_height / original_height) * original_width)

# 4. 缩放图片到新的尺寸
resized_image = image.resize((new_width, new_height))

# 5. 保存缩放后的图片为 PNG
resized_image.save(r'e:\work\苏大-鹌鹑蛋好吃\热力图\contact_transparent_03_L.png')

print("图片已成功缩放并保存")
