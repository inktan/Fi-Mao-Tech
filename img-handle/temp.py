import os  
import shutil  
  
def move_if_no_imgs(root_dir, backup_dir):  
    # 确保backup目录存在  
    if not os.path.exists(backup_dir):  
        os.makedirs(backup_dir)  
  
    for subdir, dirs, files in os.walk(root_dir):  
        if subdir == root_dir:  
            continue  # 跳过根目录本身  
  
        # 检查当前子目录是否包含imgs子目录  
        if not any(d.endswith('imgs') for d in dirs):  
            # 如果不包含，则移动到backup目录  
            # 注意：移动整个目录需要改变路径，包括子目录名  
            target_dir = os.path.join(backup_dir, os.path.basename(subdir))  
            # 如果目标目录已存在，可以选择跳过或删除原目录  
            if os.path.exists(target_dir):  
                print(f"跳过 {subdir}，因为 {target_dir} 已存在")  
                continue  
              
            shutil.move(subdir, target_dir)  
            print(f"已将 {subdir} 移动到 {target_dir}")  
  
# 使用示例  
root_dir = r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\architizer'  
backup_dir = r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\architizer-empty'  
move_if_no_imgs(root_dir, backup_dir)
