# encoding:utf-8
# 根据您选择的AK已为您生成调用代码
# 检测到您当前的AK设置了IP白名单校验
# 您的IP白名单中的IP非公网IP，请设置为公网IP，否则将请求失败
# 请在IP地址为0.0.0.0/0 外网IP的计算发起请求，否则将请求失败
import requests 

import pandas as pd  
import os  
import glob  
import os   

# 服务地址
host = "https://api.map.baidu.com"

# 接口地址
uri = "/place/v2/suggestion"

# 此处填写你在控制台-应用管理-创建应用后获取的AK
ak = "qtjtdLI2C7RaEr7PPnbg1FSJljOg4LlI"

# params = {
#     "query":    "天安门",
#     "region":    "2911",
#     "city_limit":    "true",
#     "output":    "json",
#     "ak":       ak,

# }

# response = requests.get(url = host + uri, params = params)
# if response:
#     print(response.json())

df = pd.read_csv(r'e:\work\sv_zhoujunling\建筑地名.csv', encoding='gbk')

# 创建一个空列表来存储行数据  
rows = []

# 遍历每一行数据  
for index, row in df.iterrows():  
    row_dict = row.to_dict()

    params = {
        "query":    row['address'],
        "region":    "2911",
        "city_limit":    "true",
        "output":    "json",
        "ak":       ak,
    }

    response = requests.get(url = host + uri, params = params)
    if response:
        response_result = response.json()["result"]
        print(len(response_result),'==',row['address'])
        if len(response_result) > 0:
            # print(response_result[0])
            row_dict['lng'] = response_result[0]["location"]["lng"]
            row_dict['lat'] = response_result[0]["location"]["lat"]
    else:
        row_dict['lng'] = ''
        row_dict['lat'] = ''

    rows.append(row_dict)
    # print(row_dict)

# new_df = pd.DataFrame(rows)

# new_df.to_csv(r'e:\work\sv_zhoujunling\建筑地名_lnglat.csv', index=False)
