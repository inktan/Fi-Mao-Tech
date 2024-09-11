import json
file_path = r'e:\work\sv_chenlong20240907\id_panoramas_infos_02.json'
with open(file_path, 'r', encoding='utf-8') as file:
    data05 = json.load(file)

given_list = list(data05.keys())
given_list_int = [int(item) for item in given_list]

# print(data05.keys())
print(len(data05.keys()))
main_list = list(data05.values())

from collections import defaultdict

date_year_month_counts = defaultdict(int)

# 遍历每个列表和字典
for list_of_dict in main_list:
    for d in list_of_dict:
        # 获取date_year_month的值
        # date_value = d.get("date_year_month", None)
        # date_value = d.get("year", None)
        date_value = d.get("month", None)
        # 如果date_year_month存在，则增加其计数
        if date_value:
            date_value*=12
            date_year_month_counts[date_value] += 1

# 使用sorted函数和lambda表达式进行排序
sorted_dict = dict(sorted(date_year_month_counts.items(), key=lambda item: item[1], reverse=True))
print(sorted_dict)
  
  