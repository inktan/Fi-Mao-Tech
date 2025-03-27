import json
import time

import pandas
import requests

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
                proxies=proxies
            )
            time.sleep(.4)
            return response
        except Exception as e:
            print(f"some error:{e}")
            time.sleep(2)

def crawl_area(areaname,areaid):

    for page in range(1,1000):
        url = f'https://m.anjuke.com/esf-ajax/community/list?city_id=11&page_size=25&page={page}&area_id={areaid}&is_tw=1'
        url = f'https://m.anjuke.com/sh/community/200907/'
        response = send_get(url,headers=headers,params={})

        with open(f'xxxxxxxxxxxxxxxxxxxxx.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        # .json()
        response = send_get(url,headers=headers,params={}).json()

        datalist = response.get("data",{}).get("communities",[])

        print(areaname,page,len(datalist))

        for idata in datalist:

            saveitem = {}
            saveitem["小区id"] = idata.get("base",{}).get("id")
            saveitem["详细地址"] = f'https://shanghai.anjuke.com/community/view/'+saveitem["小区id"]
            saveitem["行政区"] = idata.get("base",{}).get("areaName")
            saveitem["维度"] = idata.get("base",{}).get("blat")
            saveitem["经度"] = idata.get("base",{}).get("blng")
            saveitem["建筑楼层类型"] = idata.get("base",{}).get("buildTypeStr")
            saveitem["竣工时间"] = idata.get("base",{}).get("completionTime")
            saveitem["默认照片"] = idata.get("base",{}).get("defaultPhoto")
            saveitem["小区名"] = idata.get("base",{}).get("name")
            saveitem["住宅类型"] = idata.get("base",{}).get("shipTypeStr")
            saveitem["标签"] = idata.get("base",{}).get("tags")
            saveitem["商业区"] = idata.get("base",{}).get("tradingAreaName")
            saveitem["小区介绍"] = idata.get("extend",{}).get("introduction")
            saveitem["总户数"] = idata.get("extend",{}).get("totalHouseHoldNum")
            saveitem["水电"] = idata.get("extend",{}).get("waterPowerSupply")
            saveitem["绿化率"] = idata.get("extend",{}).get("landscapingRatio")
            saveitem["小区均价"] = idata.get("priceInfo",{}).get("price")
            saveitem["在租数"] = idata.get("propInfo",{}).get("rentNum")
            saveitem["在售数"] = idata.get("propInfo",{}).get("saleNum")

            print(areaname,page,saveitem)

            with open("./libs/data.txt",'a',encoding='utf-8') as f:
                f.write(json.dumps(saveitem))
                f.write('\n')
        if len(datalist) < 25:
            break

if  __name__ == "__main__":
    crawl_area(areaname='浦东',areaid='7')
    crawl_area(areaname='闵行',areaid='11')
    crawl_area(areaname='松江',areaid='15')
    crawl_area(areaname='宝山',areaid='13')
    crawl_area(areaname='嘉定',areaid='14')
    crawl_area(areaname='徐汇',areaid='5')
    crawl_area(areaname='青浦',areaid='19')
    crawl_area(areaname='静安',areaid='2')
    crawl_area(areaname='普陀',areaid='10')
    crawl_area(areaname='杨浦',areaid='9')
    crawl_area(areaname='奉贤',areaid='17')
    crawl_area(areaname='黄埔',areaid='4')
    crawl_area(areaname='虹口',areaid='8')
    crawl_area(areaname='长宁',areaid='6')
    crawl_area(areaname='金山',areaid='18')
    crawl_area(areaname='崇明',areaid='20')
    crawl_area(areaname='上海周边',areaid='7049')

    with open("./libs/data.txt",'r',encoding='utf-8') as f:
        lines = [json.loads(i.strip()) for i in f.readlines()]
    df = pandas.DataFrame(lines)
    df.to_excel("小区详情.xlsx",index=False)