from collections import Counter

import os
import csv

img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

folder_path = r'F:\GoogleDrive\wt282532\我的云端硬盘\sv_points_surrounding_times\sv_pan_zoom3 (1)'

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)

processed_list = []
for s in img_names:
    parts = s.split('_')
    new_element = parts[-2]+'_'+parts[-1].split('.')[0]
    processed_list.append(new_element)

# print("处理后的列表：")
# print(processed_list)

# 2. 统计每个元素的出现次数
count_dict = Counter(processed_list)

# 2. 统计出现次数并按次数降序排序
count_dict = Counter(processed_list)
sorted_items = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)

# 3. 写入CSV文件
csv_filename = r'F:\work\sv_ran\sv_pan\sv_points_surrounding_times_element_counts.csv'
with open(csv_filename, 'w', newline='', encoding='gbk') as csvfile:
    writer = csv.writer(csvfile)
    # 写入表头
    writer.writerow(['元素', '出现次数'])
    # 写入数据
    for item, count in sorted_items:
        writer.writerow([item, count])

print(f"结果已保存到 {csv_filename}")