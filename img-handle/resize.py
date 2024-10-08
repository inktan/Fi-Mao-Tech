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
folder_path = 'D:\Users\wang.tan.GOA\WeChat Files\wxid_0431434314115\FileStorage\File\2024-09\aomen'
output_folder = 'D:\Users\wang.tan.GOA\WeChat Files\wxid_0431434314115\FileStorage\File\2024-09\aomen_01'

# 2. 创建输出文件夹（如果不存在）
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 3. 遍历文件夹中的所有图片
for file_name in os.listdir(folder_path):
    if file_name.endswith(('.png', '.jpg', '.jpeg')):  # 检查是否为图片文件
        file_path = os.path.join(folder_path, file_name)

        # 4. 打开图片
        img = Image.open(file_path)

        # 5. 缩放图片到 960x960
        img_resized = img.resize((960, 960))

        # 6. 裁剪图片（上下裁剪到 960x720）
        img_cropped = img_resized.crop((0, 120, 960, 840))  # 上裁剪 120 像素，下裁剪 120 像素

        # 7. 保存裁剪后的图片
        output_path = os.path.join(output_folder, file_name)
        img_cropped.save(output_path)

print("所有图片已处理并保存到输出文件夹。")

