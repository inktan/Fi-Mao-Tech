import os  
import json  
  
def load_json_files_from_folder(folder_path):  
    """  
    加载指定文件夹中的所有JSON文件，合并它们的内容到一个字典中，  
    并自动处理重复的key。  
    """  
    merged_data = {}  
    for filename in os.listdir(folder_path):  
        if filename.endswith(".json"):  
            file_path = os.path.join(folder_path, filename)  
            with open(file_path, 'r', encoding='utf-8') as file:  
                data = json.load(file)  
                # 更新merged_data，如果key已存在，则不会改变（因为字典键唯一）  
                merged_data.update(data)
    return merged_data
  
def save_dict_to_json(data, output_file):
    """  
    将字典保存到JSON文件中。
    """
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
  
# 使用函数  
folder_path = r'E:\work\sv_chenlong20240907'  # 更改为你的JSON文件所在文件夹的路径  
output_file = r'e:\work\sv_chenlong20240907\id_panoramas_infos_02.json'  # 合并后的JSON文件保存路径  
  
merged_data = load_json_files_from_folder(folder_path)  
save_dict_to_json(merged_data, output_file)  
  
print(f"数据已合并并保存到 {output_file}")

