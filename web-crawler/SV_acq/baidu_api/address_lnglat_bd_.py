import pandas as pd
import csv
from tqdm import tqdm
from coordinate_converter import transCoordinateSystem, transBmap
import requests
import pandas as pd

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

csv_path = r'e:\work\sv_yueliang\备份小区名.csv'
df = pd.read_csv(csv_path, encoding='gbk')
csv_path = r'e:\work\sv_yueliang\备份小区名_lng_lat_01.csv'

points_df = pd.DataFrame(columns=['id','address','lng_bd09','lat_bd09','lng_gcj02', 'lat_gcj02','lng_wgs84', 'lat_wgs84'])

for i,row in enumerate(tqdm(df.iterrows())):
    # if i<81401:
    #     continue
    # if i>30000:
    #     continue

    print(i)
    input_string = '上海市' + row[1]['管理机构']

    lng_bd09, lat_bd09 = getlocation(input_string)
    lng_gcj02, lat_gcj02 = transCoordinateSystem.bd09_to_gcj02(lng_bd09, lat_bd09)
    lng_wgs84, lat_wgs84 = transCoordinateSystem.gcj02_to_wgs84(lng_gcj02, lat_gcj02)

    points_df.loc[len(points_df)] = [row[1]['id'],input_string,lng_bd09,lat_bd09,lng_gcj02, lat_gcj02,lng_wgs84, lat_wgs84]

print(points_df)
points_df.to_csv(r'e:\work\sv_yueliang\备份小区名_lng_lat_01.csv', index=False)
