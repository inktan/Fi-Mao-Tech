import os
import pandas as pd
import re

# 设定文件夹路径
folder_path = r'E:\work\sv_pangpang\sv_pano_20251219\CoS_30m_pano_cut'

# 初始化列表用于存储数据
data_list = []

# 遍历文件夹
for filename in os.listdir(folder_path):
    # 只处理 .png 文件
    if filename.lower().endswith('.png'):
        # 移除后缀名
        name_without_ext = os.path.splitext(filename)[0]
        
        # 使用正则表达式将 _ 和 - 都作为分隔符进行分割
        # 或者使用 name_without_ext.replace('-', '_').split('_')
        parts = re.split(r'[_|-]', name_without_ext)
        
        # 确保分割后的元素足够提取（至少需要4个元素）
        if len(parts) >= 4:
            id_val = parts[1]      # 第二个元素
            year_val = parts[2]    # 第三个元素
            month_val = parts[3]   # 第四个元素
            
            data_list.append({
                'filename': filename,
                'id': id_val,
                'year': year_val,
                'month': month_val
            })

# 转换为 DataFrame
df = pd.DataFrame(data_list)

# 保存为 CSV
output_path = r'E:\work\sv_pangpang\sv_pano_20251219\file_info_extracted.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"提取完成！结果已保存至: {output_path}")
print(df.head()) # 显示前几行预览