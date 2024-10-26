import os  
import shutil  
  
def move_images_with_2017(source_folder, destination_folder):  
    # 如果目标文件夹不存在，则创建它  
    if not os.path.exists(destination_folder):  
        os.makedirs(destination_folder)  
      
    # 遍历源文件夹中的所有文件  
    for filename in os.listdir(source_folder):  
        # 检查文件是否是JPG格式并且文件名中包含 "_2017"  
        if filename.lower().endswith('.jpg') and '_2017' in filename:  
            # 获取文件的完整路径  
            source_file = os.path.join(source_folder, filename)  
            destination_file = os.path.join(destination_folder, filename)  
              
            # 移动文件到目标文件夹  
            shutil.move(source_file, destination_file)  
            print(f'Moved: {source_file} -> {destination_file}')  
  
if __name__ == "__main__":  
    # 定义源文件夹和目标文件夹的路径  
    source_folder = r'E:\work\sv_levon\sv_degree_hor_new'  
    destination_folder = r'E:\work\sv_levon\sv_degree_hor_2017'  
      
    # 调用函数来移动文件  
    move_images_with_2017(source_folder, destination_folder)