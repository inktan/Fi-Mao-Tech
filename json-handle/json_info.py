import json

# 确保你的JSON文件路径是正确的
file_path = r'e:\work\sv_chenlong20240907\id_panoramas_infos_02.json'

# 使用with语句确保文件正确关闭
with open(file_path, 'r', encoding='utf-8') as file:
    data05 = json.load(file)

# 现在 data 变量包含了文件中的JSON数据
# print(data05)
print(len(data05.keys()))

  