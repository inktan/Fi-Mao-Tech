# for i in range(27414,27466):
#     print(i)

# from PIL import Image

# # 路径到您的图片文件
# image_path = r'd:\Ai-clip-seacher\strava_heatmap\imgs\img_27414_13374.jpg'  # 请替换为您的图片路径
# # 路径到您想要保存灰度图的文件
# gray_image_path = r'd:\Ai-clip-seacher\strava_heatmap\imgs01\img_27414_13374.jpg'  # 请替换为保存路径

# # 打开图片
# image = Image.open(image_path)
# # 转换为灰度图
# gray_image = image.convert('L')
# # 保存灰度图
# gray_image.save(gray_image_path)
from PIL import Image

num_cols = 27468-27414
num_rows = 13416-13374

contact_sheet = Image.new('RGB', (num_cols * 512, num_rows * 512), (255, 255, 255, 0))

x_offset = 0
y_offset = 0

for i in range(27414,27468): #X轴
    for j in range(13374,13416): #Y轴

        img_path = f'd:\Ai-clip-seacher\strava_heatmap\imgs\img_{i}_{j}.png'

        try:
            img = Image.open(img_path).convert('L')
            # contact_sheet.paste(img, (x_offset, y_offset))
            # y_offset += 512
            # if y_offset >= num_rows * 512:
            #     y_offset = 0
            #     x_offset += 512

        except Exception as e:
            print(img_path)
            # y_offset += 512
            # if y_offset >= num_rows * 512:
            #     y_offset = 0
            #     x_offset += 512

contact_sheet_path = r'D:\Ai-clip-seacher\strava_heatmap\contact_sheet_L.png'
contact_sheet.save(contact_sheet_path)