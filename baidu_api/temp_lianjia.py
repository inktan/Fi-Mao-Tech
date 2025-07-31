# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import random
import json
import re
from tqdm import tqdm

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "m.lianjia.com",
    "Pragma": "no-cache",
    "Referer": "https://clogin.lianjia.com/",
    "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}

cookies = {
    "lianjia_uuid": "61a30485-75d4-403f-a8cb-8949008e9ed6",
    "Hm_lvt_46bf127ac9b856df503ec2dbf942b67e": "1753933225",
    "HMACCOUNT": "2E252058C691871B",
    "_jzqa": "1.578712360721580200.1753933227.1753933227.1753933227.1",
    "_jzqc": "1",
    "_jzqy": "1.1753933227.1753933227.1.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6.-",
    "_jzqckmp": "1",
    "sajssdk_2015_cross_new_user": "1",
    "_ga": "GA1.2.354374190.1753933238",
    "_gid": "GA1.2.20226284.1753933238",
    "select_city": "310000",
    "crosSdkDT2019DeviceId": "rn5hdx--i8b8r9-fgqi6xr6g7i7ghp-ahf83ns5f",
    "ftkrc_": "6f59bc5a-c285-4b04-908b-b4a128c42997",
    "lfrc_": "a48c927c-70ba-44cd-b965-19055926137f",
    "_ga_LRLL77SF11": "GS2.2.s1753933316$o1$g1$t1753933321$j55$l0$h0",
    "_ga_GVYN2J1PCG": "GS2.2.s1753933316$o1$g1$t1753933321$j55$l0$h0",
    "Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e": "1753933448",
    "sensorsdata2015jssdkcross": "%7B%22distinct_id%22%3A%221985e912e85266-0cb66a1141ab3c8-26011151-2073600-1985e912e86a9f%22%2C%22%24device_id%22%3A%221985e912e85266-0cb66a1141ab3c8-26011151-2073600-1985e912e86a9f%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_utm_source%22%3A%22baidu%22%2C%22%24latest_utm_medium%22%3A%22pinzhuan%22%2C%22%24latest_utm_campaign%22%3A%22wyhz%22%2C%22%24latest_utm_content%22%3A%22biaotimiaoshu%22%2C%22%24latest_utm_term%22%3A%22biaoti%22%7D%7D",
    "Hm_lvt_28b65c68923b952bf94c102598920ce0": "1753933531",
    "session_id": "2ca8cbb6-6602-866d-abf9-cae34a149803",
    "srcid": "eyJ0Ijoie1wiZGF0YVwiOlwiMmQwNTJlN2UxNWJiZGQ2MTcwMzRkOWNmZmUwNGJjNzc2NTAxZjAyMDc3Yzg5ODgxMTQ5ODU4NzlkM2JlMzdhNjFhYTc3ZjBiNTViYWUyMzRhMjE3YzdkYmIyZjE5MDhkZmY2ZTA0NDQ5ZjQyZTlhNDgzODI4MTY4YzdkYWFjZDY4NzllMWJlYTg2NGI2NGRjNmJlYjYwMjk5NDQ2Zjc1NWJlMmI2MGYwMjQ0MjNkN2NhMTY2ODk1MTIwYjQzM2U0N2VmY2E1ZjcwYjdmNDcwOTE4NjAzNTgzYmQ2NTNmY2I0NTE2NzAwN2U0MTVkMTBlNmU5ODMxYjViMmZlZjQwMFwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCI4Y2E3YmUyNFwifSIsInIiOiJodHRwczovL20ubGlhbmppYS5jb20vc2gvZXJzaG91ZmFuZy9zZWFyY2gvIiwib3MiOiJ3ZWIiLCJ2IjoiMC4xIn0=",
    "_ga_XRDEC2G0T9": "GS2.2.s1753933532$o1$g1$t1753933796$j60$l0$h0",
    "_ga_XGP5EDPZTV": "GS2.2.s1753933532$o1$g1$t1753933796$j60$l0$h0",
    "_ga_SNG6R1B3VY": "GS2.2.s1753933532$o1$g1$t1753933796$j60$l0$h0",
    "digData": "%7B%22key%22%3A%22m_pages_ershoufangSearch%22%7D",
    "lianjia_ssid": "e2293963-4ec9-4268-97e2-e16037416b2c",
    "login_ucid": "2000000133679582",
    "lianjia_token": "2.001385d4e5711770d70228fdd46ff758fc",
    "lianjia_token_secure": "2.001385d4e5711770d70228fdd46ff758fc",
    "security_ticket": "mQtstzFmrTO9JO3+TwbIjhyCkK69hlVgpWjsBfe9wOyx1P7ra9uK5VsobVga1SqEOd6XUSHkknMNLcovZ1NgRJWGcyachc713heLZmWGr02jNfnZVRjIF3zj0/GRjq3e6QSRj72EXnUJ3RgLpgpWF8A9rW8smkqGiuWsIEY4/gk=",
    "Hm_lpvt_28b65c68923b952bf94c102598920ce0": "1753950334",
    "beikeBaseData": "%7B%22parentSceneId%22%3A%22%22%7D"
}
def get_xiaoqu_links(page_url):
    """获取小区链接"""
    try:
        response = requests.get(page_url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        xiaoqu_links = []
        for card in soup.select('div.lj-track'):
            link = card.find('a', href=True)
            if link and '/xiaoqu/' in link['href']:
                xiaoqu_links.append(link['href'])
        
        return xiaoqu_links
    except Exception as e:
        print(f"获取小区链接失败: {e}")
        return []

def get_xiaoqu_info(url):
    """获取小区详细信息"""
    
    info_dict = {}
    try:
        response = requests.get(url,headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找包含__PRELOADED_STATE__的script标签
        script_tags = soup.find_all('script')
        preloaded_state = None

        for script in script_tags:
            if '__PRELOADED_STATE__' in script.text:
                # 使用正则表达式提取JSON数据
                match = re.search(r'window\.__PRELOADED_STATE__\s*=\s*({.*?});', script.text, re.DOTALL)
                if match:
                    preloaded_state = match.group(1)
                    break

        if preloaded_state:
            try:
                # 解析JSON数据
                data = json.loads(preloaded_state)
                # 提取survey数据
                survey_data = data.get('xiaoquDetail', {}).get('survey', {})
                # 将数据转换为列表形式
                for key, item in survey_data.items():
                    info_dict[item['name']] = item['value']                
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
        else:
            print("未找到 __PRELOADED_STATE__ 数据")
        
    except Exception as e:
        print(f"获取小区信息失败 {url}: {e}")

    return info_dict

def main():
        # 从CSV文件读取地址数据
    try:
        df_input = pd.read_csv(r'e:\work\sv_kkkkatrina\小区信息_02.csv',encoding='gbk')  # 替换为你的输入文件路径
        # addresses = df_input['address'].dropna().unique()  # 假设CSV中有'address'列
        addresses = df_input['address']
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return
    
    # 收集所有小区信息
    all_data = []
    for index, address in tqdm(enumerate(addresses), mininterval=0.1, total=len(addresses), desc="处理地址"):
        # 构造搜索URL
        search_url = f"https://m.lianjia.com/sh/ershoufang/rs{str(address).replace(' ', '')}"
        print(f"正在处理地址: {address}, 搜索URL: {search_url}")
        
        # 获取小区链接
        xiaoqu_links = get_xiaoqu_links(search_url)
        # if not xiaoqu_links:
        #     print("没有找到小区链接")
        #     continue
        
        print(f"找到 {len(xiaoqu_links)} 个小区链接")

        info = {}
        for link in xiaoqu_links:
            print(f"正在处理: {link}")
            info = get_xiaoqu_info(link)
            break
            # 随机延迟，避免请求过于频繁
        
        info = {'搜索地址': address, **info}
        info = {'id': index, **info}
        all_data.append(info)

        # sleep(random.uniform(1, 3))
    
    # 保存为CSV
    if all_data:
        df = pd.DataFrame(all_data)
        # 确保列顺序一致
        columns_order = ['id', '搜索地址', '建成年代', '房屋用途', '建筑类型', '开发企业', '交易权属', 
                        '供暖类型', '用水类型', '用电类型', '固定车位数', 
                        '停车费用', '燃气费用', '容积率', '绿化率', '物业费用']
        # 只保留存在的列
        existing_columns = [col for col in columns_order if col in df.columns]
        df = df[existing_columns]
        
        df.to_csv(r'E:\work\sv_kkkkatrina\lianjia_xiaoqu_info.csv', index=False, encoding='utf_8_sig')
        print("数据已保存为 xiaoqu_info.csv")
    else:
        print("没有获取到有效数据")

if __name__ == "__main__":
    main()