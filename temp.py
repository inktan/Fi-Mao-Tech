import os
from collections import Counter

def analyze_images_in_folder(folder_path):
    # 定义常见的图片后缀名
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff')
    
    extracted_elements = []

    # 检查路径是否存在
    if not os.path.exists(folder_path):
        print(f"错误：文件夹路径 '{folder_path}' 不存在。")
        return

    # 遍历文件夹下的所有文件
    for filename in os.listdir(folder_path):
        # 1. 筛选图片文件（忽略大小写）
        if filename.lower().endswith(image_extensions):
            # 2. 去掉文件扩展名，只保留文件名部分
            name_without_ext = os.path.splitext(filename)[0]
            
            # 3. 使用 '_' 进行分割
            parts = name_without_ext.split('_')
            
            # 4. 获取分割后的倒数第二个元素
            # 注意：只有当分割后的部分至少有 2 个时，倒数第二个才存在
            if len(parts) >= 2:
                element = parts[-2]
                extracted_elements.append(element)
            else:
                print(f"跳过文件 '{filename}': 分割后不足两个元素。")

    # 5. 统计分析
    # 计算每个唯一值的出现次数
    counts = Counter(extracted_elements)
    # 计算所有提取出来的元素总数
    total_count = len(extracted_elements)

    # 打印结果
    print("-" * 30)
    print(f"统计报告：")
    print(f"处理的元素总个数: {total_count}")
    print("-" * 30)
    print("各元素出现次数（唯一值统计）:")
    for value, count in counts.items():
        print(f" - {value}: {count} 次")
    print("-" * 30)

    return counts, total_count

# --- 使用示例 ---
# 请将下面的路径替换为你电脑上真实的文件夹路径
your_folder_path = r'F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\厦门市\sv_pan01' 
analyze_images_in_folder(your_folder_path)