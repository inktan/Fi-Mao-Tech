# from PIL import Image
# Image.MAX_IMAGE_PIXELS = None  # 这将移除像素数量的限制

# # 1. 打开图片
# image = Image.open(r'e:\work\苏大-鹌鹑蛋好吃\热力图\contact_transparent_01_L.png').convert('L')  # 确保图像是灰度模式

# # 2. 获取图片的原始尺寸
# original_width, original_height = image.size

# # 3. 计算新的宽度，保持宽高比不变
# new_height = 1000
# new_width = int((new_height / original_height) * original_width)

# # 4. 缩放图片到新的尺寸
# resized_image = image.resize((new_width, new_height))

# # 5. 保存缩放后的图片为 PNG
# resized_image.save(r'e:\work\苏大-鹌鹑蛋好吃\热力图\contact_transparent_03_L.png')

# print("图片已成功缩放并保存")

from PIL import Image
import os

# 1. 指定文件夹路径
folder_path = 'E:\work\sv_卷毛彤\sv_pan'
output_folder = 'E:\work\sv_卷毛彤\sv_pan_noCar'

# 2. 创建输出文件夹（如果不存在）
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 3. 遍历文件夹中的所有图片
for file_name in os.listdir(folder_path):
    if file_name.endswith(('.png', '.jpg', '.jpeg')):  # 检查是否为图片文件
        image_path = os.path.join(folder_path, file_name)

        image = Image.open(image_path)

        # 裁剪图片顶部1450像素
        height = 1450
        cropped_image = image.crop((0, 0, image.width, height))

        # 保存裁剪后的图片
        output_path =  os.path.join(output_folder, file_name)
        cropped_image.save(output_path)


print("所有图片已处理并保存到输出文件夹。")

