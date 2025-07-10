import os

def find_car_service_shp_files(root_folder):
    """
    查找指定路径下所有以'_汽车服务.shp'结尾的文件
    
    参数:
        root_folder (str): 要搜索的根目录路径
        
    返回:
        list: 匹配的文件完整路径列表
    """
    matched_files = []
    
    # 遍历目录树
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            # 检查文件名是否以'_汽车服务.shp'结尾（不区分大小写）
            if filename.lower().endswith('_汽车服务.shp'):
                full_path = os.path.join(foldername, filename)
                matched_files.append(full_path)

    return matched_files

# 使用示例
search_path = r'E:\work\sv_kaixindian'
result_files = find_car_service_shp_files(search_path)

# 打印结果
print(f"在 {search_path} 下找到 {len(result_files)} 个匹配文件:")
for i, filepath in enumerate(result_files, 1):
    print(f"{i}. {filepath}")