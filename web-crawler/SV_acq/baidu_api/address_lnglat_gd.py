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
import math
import time

# 服务地址
host = "https://restapi.amap.com"

# 接口地址
uri = "/v3/geocode/geo"

# 此处填写你在控制台-应用管理-创建应用后获取的AK
key = "6cac8ebad7e6b8429901851d69d000de"

df = pd.read_csv(r'e:\work\sv_zhoujunling\建筑地名01.csv', encoding='gbk')
rows = []

# 遍历每一行数据  
for index, row in df.iterrows():  
    row_dict = row.to_dict()
    address = row['name']

    print(address)
    time.sleep(0.51)
    if row['name'] != '' and  not pd.isna(address):
        address = '澳门特别行政区' + address
            
        params = {
            "address": address,
            # "output": "XML",
            "key": key,
            "city":"澳门"
        }

        response = requests.get(url = host + uri, params = params)
        if response.status_code == 200:
            response_result = response.json()
            if "geocodes" in response_result:
                geocodes = response_result['geocodes']
                if len(geocodes) >= 1:
                    location = geocodes[0]["location"].split(',')
                    row_dict['lng'] = location[0]
                    row_dict['lat'] = location[1]
                else:
                    row_dict['lng'] = ''
                    row_dict['lat'] = ''

    rows.append(row_dict)
    # print(row_dict)

new_df = pd.DataFrame(rows)

new_df.to_csv(r'e:\work\sv_zhoujunling\建筑地名01_lnglat.csv', index=False)
