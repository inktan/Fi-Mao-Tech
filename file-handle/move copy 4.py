import os  
import shutil  
  
def list_directories(path):  
    try:  
        # 获取指定路径下的所有文件和文件夹  
        items = os.listdir(path)  
        directories = [os.path.join(path, item) for item in items if os.path.isdir(os.path.join(path, item))]  
        return directories  
    except Exception as e:  
        print(f"An error occurred: {e}")  
        return []  
  
path = r"E:\work\sv_j_ran\sv_pan_01"  
directories = list_directories(path)  
for directory in directories:  
    print(directory)
    
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]  
    
    # 如果目录中有文件，获取第一个文件路径  
    if files:  
        first_file_path = files[0]  
        print("第一个文件路径是:", first_file_path)  

        target_file_path = first_file_path.replace("sv_pan_01", "sv_pan_02")
        if not os.path.exists(os.path.dirname(target_file_path)):  
            os.makedirs(os.path.dirname(target_file_path))  

        shutil.move(first_file_path, target_file_path)
    else:  
        print("目录中没有文件")
