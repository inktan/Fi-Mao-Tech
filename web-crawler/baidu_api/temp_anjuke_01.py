
import time
import csv
import pandas as pd
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup

from urllib3.exceptions import InsecureRequestWarning
import urllib3
# 关闭警告
urllib3.disable_warnings(InsecureRequestWarning)

proxy_host = 'http-dynamic-S02.xiaoxiangdaili.com'
proxy_port = 10030
proxy_username = '916959556566142976'
proxy_pwd = 'qHDFwFYk'

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxy_host,
        "port": proxy_port,
        "user": proxy_username,
        "pass": proxy_pwd,
}

proxies = {
        'http': proxyMeta,
        'https': proxyMeta,
}

headers = {
    "User-Agent":'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    "Accept":'application/json, text/plain, */*, application/x-json, */*;q=0.01'
}

def send_get(url,headers,params):
    while 1:
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=(4,5),
                verify=False,
                # proxies=proxies
            )
            time.sleep(.4)
            return response
        except Exception as e:
            print(f"some error:{e}")
            time.sleep(2)

def get_info(address):
    url = f'https://m.anjuke.com/esf-ajax/community/autocomplete?city_id=11&kw={address}&type=2'
    print(url)
    response = send_get(url,headers=headers,params={}).json()
    datalist = response.get("data",[])
    if len(datalist) == 0:
        return ''
    
    id = datalist[0].get('id')
    # if str(id)=="12172":
    #     return []
    url = f'https://m.anjuke.com/sh/community/{id}/'
    print(url)
    response = send_get(url,headers=headers,params={})
    # print(response.status_code)
    # print(response.text)

    info_dict = {}

    soup = BeautifulSoup(response.text, 'lxml')
    info_list = soup.find_all('li', class_='col-2')
    for item in info_list:
        key = item.find('span', class_='base-info-key').get_text()
        value = item.find('span', class_='base-info-value').get_text()
        info_dict[key] = value

    # 用于网页验证，不可以注释该行代码
    list(info_dict.values())[1]
    # 查找class为highlight的元素
    highlight_element = soup.find(class_='highlight')
    # 提取元素的文本内容
    highlight_text = highlight_element.get_text(strip=True).replace('元/㎡', '')

    result = list(info_dict.values())
    result.append(highlight_text)
    return result

if __name__ == '__main__':
    
    csv_path = r'e:\work\sv_yueliang\备份小区名_lng_lat_住宅区_别墅区.csv'
    # df = pd.read_csv(csv_path, encoding='gbk')
    df = pd.read_csv(csv_path)

    points_df = pd.DataFrame(columns=['id','address','address_01','lng','lat','所属商圈', '开发商', '物业公司', '小区名称', '物业类型', '竣工时间', '绿化率', '容积率', '建筑面积', '总户数', '小区地址', '停车位', '物业费', '挂牌均价'])
    for i,row in enumerate(tqdm(df.iterrows())):
        # if i<1997:
        #     continue
        # if i>=20000:
        #     continue
        print(i)

        id = row[1]['id']
        address = row[1]['name']
        # lng = row[1]['lng_wgs84']
        # lat = row[1]['lat_wgs84']
        temp = ['','','','','','', '', '', '', '', '', '', '', '', '', '', '', '', '']
        if not isinstance(address,str):
            points_df.loc[len(points_df)] = temp
            continue
        if address == '0':
            points_df.loc[len(points_df)] = temp
            continue
        if address == 0:
            points_df.loc[len(points_df)] = temp
            continue

        if address.endswith("号"):
            address = address[:-1] + "弄"

        address_01 = address[:-1]
        if '街道' in address_01:
            address_01 = address_01.split('街道')[-1]
        elif '镇' in address_01:
            address_01 = address_01.split('镇')[-1]
        elif '工业区' in address_01:
            address_01 = address_01.split('工业区')[-1]
        elif '上海市' in address_01:
            address_01 = address_01.split('上海市')[-1]

        if not isinstance(address_01,str):
            points_df.loc[len(points_df)] = temp
            continue

        rate_list = [id,address,address,'lng','lat']

        while True:
            # count+=1
            # if count>90:
            #     return
            try:
                infos = get_info(address)
                break
            except Exception as e:
                print(f"请判断 m.anjuke 是否需要验证,{e}")
                print("Connection error. Trying again in 2 seconds.")
                time.sleep(2)

        if len(infos) == 0:
            points_df.loc[len(points_df)] = temp
            continue
        else:
            rate_list.extend(infos)
            # print(rate_list)

        points_df.loc[len(points_df)] = rate_list
        
        if i%100 == 0:
            points_df.to_csv(r'e:\work\sv_yueliang\备份小区名_lng_lat_anjuke_01.csv', index=False)

points_df.to_csv(r'e:\work\sv_yueliang\备份小区名_lng_lat_anjuke_01.csv', index=False)

