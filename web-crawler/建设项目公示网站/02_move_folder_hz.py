import os
import shutil

def move_folders_with_keyword(source_dir, target_dir, keywords):
    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)

    # 遍历源文件夹中的所有子文件夹
    for folder_name in os.listdir(source_dir):
        folder_path = os.path.join(source_dir, folder_name)
        
        # 检查是否是文件夹且名称包含"徐汇区"
        if os.path.isdir(folder_path) and any(keyword in folder_name for keyword in keywords) :
            # 构造目标路径
            target_path = os.path.join(target_dir, folder_name)

            # 移动文件夹
            try:
                shutil.move(folder_path, target_path)
                print(f"已移动: {folder_path} -> {target_path}")
            except Exception as e:
                print(f"移动 {folder_name} 时出错: {str(e)}")

    print("操作完成。")

# 源文件夹路径
source_dir = r'Y:\GOA-项目公示数据\建设项目公示信息\杭州\杭州市\未分类项目'

# 定义所有区和对应的关键字
districts = {
    "住宅类": ["住宅", "住房", "公租房"],
    "公建类": ["商业", "公寓", "幼儿园", "老年活动中心",],
    # 可以继续添加其他区...
}

# 遍历所有区并移动文件夹
for district, keyword in districts.items():
    target_dir = f'Y:\GOA-项目公示数据\建设项目公示信息\杭州\杭州市\{district}'
    print(f"\n正在处理: {district}...")
    move_folders_with_keyword(source_dir, target_dir, keyword)

print("\n所有区处理完成。")
