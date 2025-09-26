import os
import csv
from datetime import datetime

# 获取当前日期和时间
now = datetime.now()
print("当前时间:", now)
# img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

folder_path = r'E:\stree_view'

# rate_list = ['index','osm_id','longitude','latitude','angle','date']
rate_list = ['index']
image_ss_csv = r'E:\sv_pan_names.csv'
with open('%s' % image_ss_csv ,'w',encoding='utf-8' ,newline='') as f:
    writer = csv.writer(f)
    writer.writerow(rate_list)

count = 0
print(count)
for root, dirs, files in os.walk(folder_path):
    for filename in files:
        if filename.endswith(accepted_formats):
            # file_path = os.path.join(root, filename)
            # img_paths.append(file_path)
            # img_names.append(filename)
            
            # rate_list = filename.split('_')
            rate_list = [filename]
            count+=1
            if count%5000==0:
                print(count)
                now = datetime.now()
                time_only = now.strftime("%H:%M:%S")
                print("当前时间:", time_only)
            # rate_list[-1] = rate_list[-1].split('.')[0]

            with open('%s' % image_ss_csv ,'a',encoding='utf-8' ,newline='') as f:
                writer = csv.writer(f)
                writer.writerow(rate_list)

print(len(img_names))
# for i in img_paths:
#     print(i)

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

# number_list = []
# for s in img_names:
#     try:
#         # 尝试分割并转换
#         number = int(s.split("_")[0])
#         number_list.append(int(number))
#     except (IndexError, ValueError):
#         # 如果分割失败或转换失败，跳过该字符串
#         print(f"跳过无效字符串: {s}")

# # print(number_list)

# # 生成从 1 到 21515 的整数列表
# integer_list = list(range(1, 21516))

# # 输出结果
# # print(integer_list)

# # 使用集合差集操作找到 list1 中存在但 list2 中不存在的元素
# result = list(set(integer_list) - set(number_list))

# # 输出结果
# print(len(result))




