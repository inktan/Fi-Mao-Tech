import shutil  
import os  
  
folder_path = r'E:\work\苏大-鹌鹑蛋好吃\20220720-上海'  
  
if os.path.exists(folder_path):  
    shutil.rmtree(folder_path)  
    print(f"文件夹 '{folder_path}' 已成功删除。")
else:  
    print(f"文件夹 '{folder_path}' 不存在。")