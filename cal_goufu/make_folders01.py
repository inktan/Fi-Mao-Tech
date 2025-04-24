import os
import os
import shutil

def delete_non_add_files(folder_path):
    """
    删除文件夹中所有不包含'smoothed'的文件和空子文件夹
    但保留子文件夹中文件名包含'smoothed'的文件
    
    参数:
        folder_path: 要清理的文件夹路径
    """
    for root, dirs, files in os.walk(folder_path, topdown=False):
        # 处理文件
        for file in files:
            file_path = os.path.join(root, file)
            if 'smoothed' not in file.lower():  # 不区分大小写
                try:
                    os.remove(file_path)
                    print(f"已删除文件: {file_path}")
                except Exception as e:
                    print(f"删除文件失败 {file_path}: {e}")
        
        # 处理空文件夹 (在文件处理后进行)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                if not os.listdir(dir_path):  # 如果文件夹为空
                    os.rmdir(dir_path)
                    print(f"已删除空文件夹: {dir_path}")
            except Exception as e:
                print(f"删除文件夹失败 {dir_path}: {e}")


years = ['98','99','00',
'01','02','03','04','05','06','07','08','09','10',
'11','12','13','14','15','16','17','18','19','20',
'22','23',]

for year in years:
    print(year)
    try:
        # 设置路径
        folder_to_clean = f'E:\\work\\sv_goufu\\MLP-bird-count\\year{year}'
        delete_non_add_files(folder_to_clean)
        print("清理完成！")

    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")