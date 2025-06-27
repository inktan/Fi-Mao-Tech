import os
import shutil

def delete_year_folders(folder_path):
    # 检查文件夹路径是否存在
    if not os.path.exists(folder_path):
        print(f"错误：文件夹路径 '{folder_path}' 不存在")
        return

    # 生成要匹配的年份字符串列表，如 ["2000年", "2001年", ..., "2024年"]
    years_to_delete = [f"{year}年" for year in range(2000, 2025)]
    print(f"将删除包含以下年份的文件夹: {years_to_delete}")

    # 遍历文件夹下的所有子文件夹
    for folder_name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, folder_name)
        
        # 检查是否是文件夹
        if os.path.isdir(full_path):
            # 检查文件夹名是否包含要删除的年份
            if any(year in folder_name for year in years_to_delete):
                try:
                    shutil.rmtree(full_path)  # 删除文件夹及其所有内容
                    print(f"已删除文件夹: {full_path}")
                except Exception as e:
                    print(f"删除文件夹 {full_path} 时出错: {e}")

# 使用示例
folder_path = r"Y:\GOA-项目公示数据\公众号\建筑芝士"  # 替换为你的文件夹路径
delete_year_folders(folder_path)