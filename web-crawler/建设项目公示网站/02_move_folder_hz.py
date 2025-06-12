import os
import shutil

def move_folders_with_keyword(source_dir, target_dir, district,keyword):
    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)

    # 遍历源文件夹中的所有子文件夹
    for folder_name in os.listdir(source_dir):
        folder_path = os.path.join(source_dir, folder_name)
        
        # 检查是否是文件夹且名称包含"徐汇区"
        if os.path.isdir(folder_path) and keyword in folder_name:
            # 构造目标路径
            # target_path01 = os.path.join(target_dir,district)
            target_path02 = os.path.join(target_dir,district, folder_name)
            
            # 检查目标路径是否已存在同名文件夹
            # if os.path.exists(target_path02):
            #     print(f"警告: 目标路径已存在同名文件夹 '{folder_name}'，跳过移动。")
            #     continue
            
            # 移动文件夹
            try:
                shutil.move(folder_path, target_path02)
                print(f"已移动: {folder_name} -> {target_dir}")
            except Exception as e:
                print(f"移动 {folder_name} 时出错: {str(e)}")

    print("操作完成。")

# 源文件夹路径
source_dir = r'Y:\GOA-项目公示数据\建设项目公示信息\杭州\杭州市\住宅类611'

# 定义所有区和对应的关键字
districts = {
    "住宅类": "住宅",
    "商业类": "商业",
    # "虹口区": "虹口区",
    # "杨浦区": "杨浦区",
    # 可以继续添加其他区...
}

# 遍历所有区并移动文件夹
for district, keyword in districts.items():
    target_dir = f'Y:\GOA-项目公示数据\建设项目公示信息\杭州\杭州市'
    print(f"\n正在处理: {district}...")
    move_folders_with_keyword(source_dir, target_dir,district, keyword)

print("\n所有区处理完成。")
