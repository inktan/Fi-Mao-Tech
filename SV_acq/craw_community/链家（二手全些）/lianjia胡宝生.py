#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "Brady Hu"
# __date__ = ""

import pymongo
import requests
from bs4 import BeautifulSoup
from requests import RequestException
import math
import time
import re
from multiprocessing import Pool

client = pymongo.MongoClient("localhost:27017")
db = client['lianjia']

def req(url):
    headers = {"User_Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
               "Cookie":"ljref=pc_sem_baidu_ppzq_x; select_city=110000; all-lj=6341ae6e32895385b04aae0cf3d794b0; lianjia_ssid=0dfae07f-c329-491e-a22d-9b75b6f38e77; lianjia_uuid=018970d2-5b8b-4ec3-b2bc-699f201cbf2d; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1513064878; UM_distinctid=16049b1d1aca07-075f5675bce547-5a442916-1fa400-16049b1d1ad81b; CNZZDATA1253477573=408862788-1513059858-null%7C1513059858; CNZZDATA1254525948=1811539109-1513061598-null%7C1513061598; CNZZDATA1255633284=927642908-1513061417-null%7C1513061417; CNZZDATA1255604082=363254508-1513063190-null%7C1513063190; _jzqa=1.610201458898387500.1513064879.1513064879.1513064879.1; _jzqc=1; _jzqy=1.1513064879.1513064879.1.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6%E7%BD%91.-; _jzqckmp=1; _qzjc=1; _smt_uid=5a2f89ae.4d856cef; _ga=GA1.2.1323899617.1513064881; _gid=GA1.2.883265746.1513064881; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1513064916; _qzja=1.1769319951.1513064878636.1513064878636.1513064878637.1513064903436.1513064916061.0.0.0.6.1; _qzjb=1.1513064878636.6.0.0.0; _qzjto=6.1.0; _jzqb=1.6.10.1513064879.1"}
    while True:
        try:
            webdata  = requests.get(url,headers=headers,proxies=get_proxy(),timeout = 3)
            if webdata.status_code == 200:
                return webdata.text
            else:
                pass
        except RequestException as e:
            print(e.args)

sheet_area = db['area']
def crawl_area():
    start_url = 'https://bj.lianjia.com/xiaoqu/'

    webdata = req(start_url)
    soup = BeautifulSoup(webdata,"lxml")
    areas = soup.select('div[data-role="ershoufang"]  > div:nth-of-type(1) > a')
    for item in areas:
        area = item.get_text()
        url = "https://bj.lianjia.com"+item.get("href")
        data = {"area":area,
                "url":url}
        sheet_area.insert_one(data)

sheet_xiaoqu = db['xiaoqu']
def crawl_xiaoqu():
    #判断网页页数
    for item in sheet_area.find({}):
        url = item['url']
        area = item['area']
        webdata = req(url)
        soup = BeautifulSoup(webdata,'lxml')
        xiaoqu_num = soup.select("h2.total.fl span")[0].get_text().strip()
        xiaoqu_num = int(xiaoqu_num)
        page_no = math.ceil(xiaoqu_num/30)
        for page in range(1,page_no+1):
            crawl_xiaoqu_page(area,page,url)

def crawl_xiaoqu_page(area,page,url):
    req_url  = '{}pg{}/'.format(url,str(page))
    webdata = req(req_url)
    soup = BeautifulSoup(webdata,'lxml')
    items = soup.select("ul.listContent li div.title a")
    for item in items:
        xiaoqu = item.get_text()
        url = item.get("href")
        data = {"xiaoqu":xiaoqu,
                "url":url,
                "area":area}
        if len([i for i in sheet_xiaoqu.find({"url":url})])>0:
            pass
        else:
            sheet_xiaoqu.insert_one(data)

    write_log("{}----{}----sucess".format(log_time(),req_url))

sheet_basic_info = db['basic_info']
def crawl_basic_info(area, xiaoqu, id):
    url = "https://bj.lianjia.com/xiaoqu/{}/".format(id)
    webdata = req(url)
    soup = BeautifulSoup(webdata,'lxml')
    xiaoquinfo = dict()
    xiaoquinfo['area']=area
    xiaoquinfo['id']=id
    xiaoquinfo['name']=xiaoqu
    price = soup.select("div.xiaoquPrice div.fl")[0].get_text()
    xiaoquinfo['price']=price
    xiaoquInfoitems = soup.select('div.xiaoquInfoItem')
    for item in xiaoquInfoitems:
        label = item.select("span.xiaoquInfoLabel")[0].get_text()
        content = item.select("span.xiaoquInfoContent")[0].get_text()
        xiaoquinfo[label]=content
    lnglat = re.findall("resblockPosition:'(.*?)'",webdata)[0]
    xiaoquinfo['lnglat']=lnglat
    write_log("{}----{}---crawl basic info sucess".format(log_time(),xiaoqu))
    sheet_basic_info.insert_one(xiaoquinfo)

sheet_huxing = db['huxing']
def crawl_huxing(area, xiaoqu, id):
    url = 'https://bj.lianjia.com/xiaoqu/{}/huxing/'.format(id)
    webdata = req(url)
    soup = BeautifulSoup(webdata,'lxml')
    huxing_num = int(soup.select('div.frameListRes.clear div.fl span')[0].get_text())
    page_no = math.ceil(huxing_num/10)
    for page in range(1,page_no+1):
        url_ = url+"pg{}/".format(page)
        webdata_ = req(url_)
        soup_ = BeautifulSoup(webdata_,'lxml')
        huxings = soup_.select('div.frameListItem')
        for huxing in huxings:
            fr = huxing.select("div.fr > a")[0].get_text()
            frameItemInfo = huxing.select("div.frameItemInfo")[0].get_text()
            frameItemSell = huxing.select("div.frameItemSell")[0].get_text()
            frameItemTotalPrice = huxing.select('div.frameItemTotalPrice span')[0].get_text()
            data = {"fr": fr,
                    "frameItemInfo": frameItemInfo,
                    "frameItemSell": frameItemSell,
                    "frameItemTotalPrice": frameItemTotalPrice,
                    "area": area,
                    "xiaoqu": xiaoqu}
            sheet_huxing.insert_one(data)
    write_log("{}----{}----crawl huxing info sucess".format(log_time(),xiaoqu))

sheet_ershoufang  = db['ershoufang']
def crawl_ershoufang(area, xiaoqu, id):
    url  = "https://bj.lianjia.com/ershoufang/c{}/".format(id)
    webdata = req(url)
    soup = BeautifulSoup(webdata, 'lxml')
    ershoufang_num = int(soup.select("h2.total.fl span")[0].get_text())
    page_no = math.ceil(ershoufang_num/30)
    for page in range(1,page_no+1):
        url_ = 'https://bj.lianjia.com/ershoufang/pg{}c{}/'.format(page,id)
        webdata_ = req(url_)
        soup_ = BeautifulSoup(webdata_,'lxml')
        ershoufangs = soup_.select('ul.sellListContent li.clear div.info.clear')
        for ershoufang in ershoufangs:
            title = ershoufang.select('div.title a.')[0].get_text()
            xiaoqu_address = ershoufang.select('div.address div.houseInfo a')[0].get_text()
            houseInfo = ershoufang.select('div.address div.houseInfo')[0].get_text()
            positionInfo = ershoufang.select('div.positionInfo')[0].get_text()
            followInfo = ershoufang.select('div.followInfo')[0].get_text()
            tag = {}
            for item in ershoufang.select('div.tag span'):
                tag[item.get("class")[0]]=item.get_text()
            totalPrice = ershoufang.select('div.priceInfo div.totalPrice')[0].get_text()
            unitPrice = ershoufang.select('div.priceInfo div.unitPrice')[0].get_text()
            data = {"title": title,
                    "xiaoqu_address": xiaoqu_address,
                    "houseInfo": houseInfo,
                    "positionInfo": positionInfo,
                    "followInfo": followInfo,
                    "tag": tag,
                    "totalPrice": totalPrice,
                    "unitPrice": unitPrice,
                    "area": area,
                    "xiaoqu": xiaoqu}
            sheet_ershoufang.insert_one(data)
    write_log("{}----{}----crawl ershoufang info sucess".format(log_time(), xiaoqu))

sheet_chengjiao = db['chengjiao']
def crawl_chengjiao(area, xiaoqu, id):
    url = 'https://bj.lianjia.com/chengjiao/c{}/'.format(id)
    webdata = req(url)
    soup = BeautifulSoup(webdata, 'lxml')
    ershoufang_num = int(soup.select("div.total.fl span")[0].get_text())
    page_no = math.ceil(ershoufang_num / 30)
    for page in range(1, page_no + 1):
        url_ = 'https://bj.lianjia.com/chengjiao/pg{}c{}/'.format(page, id)
        webdata_ = req(url_)
        soup_ = BeautifulSoup(webdata_, 'lxml')
        chengjiaos = soup_.select('ul.listContent li div.info')
        for chengjiao in chengjiaos:
            title = chengjiao.select('div.title')[0].get_text()
            houseInfo = chengjiao.select('div.houseInfo span')[0].get_text()
            dealDate = chengjiao.select('div.dealDate')[0].get_text()
            totalPrice = chengjiao.select('div.totalPrice')[0].get_text()
            positionInfo = chengjiao.select('div.positionInfo')[0].get_text()
            source = chengjiao.select('div.source')[0].get_text()
            unitPrice = chengjiao.select('div.unitPrice')[0].get_text()
            dealHouseInfo = [i.get_text() for i in chengjiao.select('div.dealHouseInfo span.dealHouseTxt span')]
            dealCycleInfo = [i.get_text() for i in chengjiao.select('div.dialCycleeInfo span.dealCycleTxt span')]
            data = {"title": title,
                    "houseInfo": houseInfo,
                    "dealDate": dealDate,
                    "totalPrice": totalPrice,
                    "positionInfo": positionInfo,
                    "source": source,
                    "unitPrice": unitPrice,
                    "dealHouseInfo": dealHouseInfo,
                    "dealCycleInfo": dealCycleInfo,
                    "area": area,
                    "xiaoqu": xiaoqu}
            sheet_chengjiao.insert_one(data)
    write_log("{}----{}----crawl chengjiao info sucess".format(log_time(), xiaoqu))

sheet_zufang = db['zufang']
def crawl_zufang(area, xiaoqu, id):
    url = 'https://bj.lianjia.com/zufang/c{}/'.format(id)
    webdata = req(url)
    soup = BeautifulSoup(webdata, 'lxml')
    ershoufang_num = int(soup.select("div.list-head.clear h2 span")[0].get_text())
    page_no = math.ceil(ershoufang_num / 30)
    for page in range(1, page_no + 1):
        url_ = 'https://bj.lianjia.com/zufang/pg{}c{}/'.format(page, id)
        webdata_ = req(url_)
        soup_ = BeautifulSoup(webdata_, 'lxml')
        zufangs = soup_.select('ul.house-lst li div.info-panel')
        for zufang in zufangs:
            title = zufang.select('h2 > a')[0].get_text()
            where = {}
            for item in zufang.select('div.col-1 div.where span'):
                try:
                    where[item.get('class')[0]] = item.get_text().strip()
                except TypeError:
                    pass
            direction = zufang.select('div.col-1 div.where span')[-1].get_text()
            where['direction'] = direction
            other = zufang.select('div.col-1 div.other')[0].get_text()
            label = {}
            for item in zufang.select('div.col-1 div.chanquan div.left > span')[1::2]:
                label[item.get('class')[0]]=item.get_text()
            price = zufang.select('div.col-3 div.price')[0].get_text()
            price_pre = zufang.select('div.col-3 div.price-pre')[0].get_text()
            square = zufang.select('div.col-2 div.square')[0].get_text()
            data = {"title": title,
                    "where": where,
                    "other": other,
                    "price": price,
                    "price_pre": price_pre,
                    "square": square,
                    "area": area,
                    "xiaoqu": xiaoqu}
            sheet_zufang.insert_one(data)
    write_log("{}----{}----crawl zufang info sucess".format(log_time(), xiaoqu))

def crawl_a_xiaoqu():
    list_ = []
    with open("xiaoqu (lianjia).csv",'r',encoding='utf-8') as f:
        for item in f.readlines()[1:]:
            count,id_,area, url, xiaoqu = item.strip().split(',')
            list_.append({"area":area,
                         "url":url,
                         "xiaoqu":xiaoqu})
    for item in list_:
        _crawl(item)

def _crawl(item):
    area = item['area']
    url = item['url']
    xiaoqu = item['xiaoqu']
    id = url.split('/')[-2]

    crawl_basic_info(area, xiaoqu, id)
    # crawl_huxing(area, xiaoqu, id)
    crawl_ershoufang(area, xiaoqu, id)
    # crawl_chengjiao(area, xiaoqu, id)
    crawl_zufang(area, xiaoqu, id)


def write_log(str):
    print(str)
    with open("log.log",'a',encoding='utf-8') as f:
        f.write(str+'\n')

def log_time():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

def get_proxy():
    url = 'http://api.ip.data5u.com/dynamic/get.html?order=44b365bd1275e9f6a0d15b720526f4d4&sep=3'
    while True:
        try:
            webdata = requests.get(url)
            if webdata.status_code == 200:
                return {"https":"https://{}".format(webdata.text.strip())}
            else:
                pass
        except RequestException:
            pass

def main():
    crawl_a_xiaoqu()

if __name__ == "__main__":
    main()