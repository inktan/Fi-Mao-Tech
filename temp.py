import os
import pandas as pd

def process_images_to_csv(folder_path, output_csv):
    data_list = []
    
    # 支持的图片后缀
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    
    # 1. 使用 os.walk 遍历文件夹（包括子文件夹）
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 检查是否为图片文件
            if file.lower().endswith(valid_extensions):
                # 2. 去掉后缀并使用 _ 分割
                # 例如: 0_135.52_34.68_102.34_2016_4_0.jpg -> [0, 135.52, 34.68, 102.34, 2016, 4, 0]
                file_name_without_ext = os.path.splitext(file)[0]
                split_parts = file_name_without_ext.split('_')
                
                # 将分割后的数据添加到列表
                data_list.append(split_parts)
    
    # 3. 统计并打印图片数量
    print(f"共找到图片文件数量: {len(data_list)}")
    
    if len(data_list) > 0:
        # 4. 创建 DataFrame 并指定列名
        # 注意：请确保文件名分割后的段数与列名数量匹配
        columns = ['index', 'lon', 'lat', 'heading_degree', 'year', 'month']
        
        # 如果某些文件名分割后长度不一致，这里会报错，建议先预览数据
        df = pd.DataFrame(data_list, columns=columns)
        
        # 5. 保存为 CSV
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"处理完成，结果已保存至: {output_csv}")
    else:
        print("未发现匹配的图片文件。")

# --- 使用示例 ---
target_folder = r'F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\澳门特别行政区\svi_google'  # 替换为你的实际文件夹路径
output_file = r'F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\澳门特别行政区\svi_google_image_data_info.csv'        # 结果文件名

process_images_to_csv(target_folder, output_file)