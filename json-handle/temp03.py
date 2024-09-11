import json
file_path = r'e:\work\sv_chenlong20240907\id_panoramas_infos_02.json'
with open(file_path, 'r', encoding='utf-8') as file:
    data05 = json.load(file)

given_list = list(data05.keys())
given_list_int = [int(item) for item in given_list]

# print(data05.keys())
print(len(data05.keys()))
main_list = list(data05.values())

# empty_lists_count = sum(1 for sublist in main_list if not sublist)
# print(empty_lists_count)


from collections import defaultdict

date_year_month_counts = defaultdict(int)

count = 0

# 遍历每个列表和字典
for list_of_dict in main_list:
    years = [item.get("year", None) for item in list_of_dict]

    has_01 = any(n in [2013, 2012, 2011] for n in years)  
    has_02 = any(n in [2021, 2022, 2023] for n in years)  
    if has_01 and has_02:
        count += 1

        # print(years)
        # date_year_month_counts[date_value] += 1

# 使用sorted函数和lambda表达式进行排序
# sorted_dict = dict(sorted(date_year_month_counts.items(), key=lambda item: item[1], reverse=True))
# print(len(sorted_dict.keys()))
# print(sorted_dict)
print(count)
  