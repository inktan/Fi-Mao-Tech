import os

img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

for root, dirs, files in os.walk(r'Y:\GOA-AIGC\98-goaTrainingData\Arch_200px_\淘宝效果图资源\01-效果图意向(图多，非会员分开转存)'):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)
print(len(img_names))
for i in img_paths:
    print(i)

# 每个点4张街景，共1259360张街景

# ids = []
# for file_name in img_names:
#     # 使用'_'分割文件名
#     parts = file_name.split('_')
#     # 假设ID是分割后的第一个部分
#     id_ = parts[0]
#     # 将ID添加到列表中
#     ids.append(id_)

# len(ids)