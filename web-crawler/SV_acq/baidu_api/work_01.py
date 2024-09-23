# ID
# 居住路（号）
# 经纬度

# 小区的名字
# 均价
# 竣工时间
# 总户数
# 建筑面积
# 建筑面积/总户数
# 容积率
# 绿化率
# 停车位比
# 物业费（元）

# 公园广场个 = 统计该点周边的公园与广场总个数，统计半径为多大
# 运动场馆 = 统计该点周边的运动/场馆总个数，统计半径为多大
# 确定最近公园及其距离  
# 确定最近医院及其距离
# 商场数量 = 统计该点周边的运动/场馆总个数，统计半径为多大
# 确定最近公交车站及其距离
# 车站数量 = 统计该点周边的车站（这个车站指的是公交车站？）总个数，统计半径为多大

import pandas as pd
import csv
from tqdm import tqdm
import requests

def getlocation(address):
    # 接口地址
    url = "https://api.map.baidu.com/geocoding/v3"

    # 此处填写你在控制台-应用管理-创建应用后获取的AK
    ak = 'qtjtdLI2C7RaEr7PPnbg1FSJljOg4LlI'
    params = {
        "address":address,
        "output":"json",
        "ak":ak,
    }

    response = requests.get(url=url, params=params)
    if response:
        temp = response.json()
        if temp['status'] == 0:
            return temp['result']['location']['lng'], temp['result']['location']['lat'] #获取经纬度
        else:
            return 'miss','miss'
    else:
        return 'miss','miss'

csv_path = r'f:\shanghaijiaoda_poi_shp\20240614\work03.csv'
df = pd.read_csv(csv_path)
csv_path = r'f:\shanghaijiaoda_poi_shp\20240614\work03_address_lng_lat_01.csv'

# with open(csv_path ,'w',encoding='utf-8' ,newline='') as f:
#     writer = csv.writer(f)
#     writer.writerow(['id','address','lng','lat'])
    
for i,row in enumerate(tqdm(df.iterrows())):
    if i<81401:
        continue
    # if i>30000:
    #     continue
    print(i)
    input_string = row[1]['address']

    lng,lat = getlocation(input_string)
    rate_list = [row[1]['id'],input_string,lng,lat]

    with open(csv_path ,'a',encoding='utf-8' ,newline='') as f:
        writer = csv.writer(f)
        writer.writerow(rate_list)


