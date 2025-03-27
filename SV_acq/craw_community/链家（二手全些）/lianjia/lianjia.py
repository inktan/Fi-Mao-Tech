#! /usr/local/bin/python3.0
# coding: utf-8
# -------------------------------------------------------------------------------
# Name:        LianJiaSpider
# Purpose:
#
# Author:      Yong
#
# Created:     10/12/2017
# Copyright:   (c) Yong 2017
# Licence:     <your licence>
# -------------------------------------------------------------------------------


import re
import time
import requests
from bs4 import BeautifulSoup
from requests import RequestException
import transCoordinateSystem
from settings import *

# list_key is used to save the keywords of each record
list_key = ["lianjia_id", "title", "deal_time", "longitude", "latitude", "total_price",
            "unit_price", "asking_price", "trans_period", "price_num", "watch_num",
            "focus_num", "click_num", "house_type", "floor", "floor_area",
            "house_structure", "inner_area", "building_type", "orientation",
            "built_year", "decoration", "building", "heating", "elevator_ratio",
            "property_period", "elevator", "lianjia", "property_type", "release_date",
            "use", "two_years", "shared_owner"]

# url_list is used to save all of the records
uid_key = ["name", "uid", "count", "url_list"]


def req(method, url, **kwargs):
    """
    自定义请求，用以控制headers和请求其他设置（代理、延时等）
    :param method，请求方法，如get,post等:
    :param url请求url:
    :param kwargs请求参数，如post的表单，get的params都可以放进来，看需求:
    :return 返回请求的网页文本:
    """
    while True:
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        try:
            # current_proxy = {"http": get_proxy()}
            # print(current_proxy)
            # webdata = requests.request(method,url,headers = headers,proxies=current_proxy,timeout = 3,**kwargs)
            webdata = requests.request(method, url, headers=headers, timeout=3, **kwargs)
            if webdata.status_code == 200:
                if "too many request" in webdata.text:
                    time.sleep(5)
                    pass
                else:
                    return webdata.text
            else:
                print(webdata.status_code, webdata.url)
        except RequestException:
            print("request error")
            pass


def get_proxy():
    """
    代理程序接口，用于请求代理
    :return:
    """
    proxy_url = "your proxy"
    while True:
        try:
            webdata = requests.request('get', proxy_url)
            if webdata.status_code == 200:
                return webdata.text.split(',')[0]
        except Exception as e:
            print("get new proxy failed " + str(e.args))


def get_url_list(name, uid):
    url = r"https://cd.lianjia.com/chengjiao/c{}/".format(uid)
    print(url)
    results = req("get", url)
    fields = []  # xiaoqu
    url_list = []  # chengjiao
    current_page = 1  # 还要考虑成交为0的情况

    soup = BeautifulSoup(results, "lxml")
    contents = soup.find('div', {'class', 'total fl'})
    count = contents.span.text.strip()
    if float(count) > 10000:
        write_log("{} request error".format(uid))
        pass
    elif float(count) == 0:
        write_log("{} has no records".format(uid))
        pass
    else:
        fields.extend([name, uid, count])

        for tr in soup.findAll('div', {'class': 'info'}):
            lianjia_id = tr.div.a.get('href'). \
                replace("https://cd.lianjia.com/chengjiao/", ""). \
                replace(".html", "")
            url_list.append(lianjia_id)

        page_box = soup.find('div', {'class': 'page-box house-lst-page-box'}).get('page-data')
        total_page = eval(page_box)['totalPage']  # Get total pages

        if total_page > current_page:  # get url list from the next few pages
            for next_page in range(2, total_page + 1, 1):
                url = r"https://cd.lianjia.com/chengjiao/pg{}c{}/".format(next_page, uid)
                results = req("get", url)
                soup = BeautifulSoup(results, "lxml")
                for tr in soup.findAll('div', {'class': 'info'}):
                    lianjia_id = tr.div.a.get('href'). \
                        replace("https://cd.lianjia.com/chengjiao/", ""). \
                        replace(".html", "")
                    url_list.append(lianjia_id)

        str = (',').join(url_list)
        fields.append(str)

        data = dict(zip(uid_key, fields))
        sheet_list.insert_one(data)


def get_info(lianjia_id):
    url = r"https://cd.lianjia.com/chengjiao/{}.html".format(lianjia_id)
    results = req("get", url)
    field = []
    field.append(lianjia_id)

    soup = BeautifulSoup(results, "lxml")

    house_title = soup.find('div', {'class': 'house-title'})  # Title, Deal time
    title = house_title.div.h1.text.replace(' ', ',')
    deal_time = house_title.div.span.text.replace(' ', ',')
    field.extend([title, deal_time])

    regex = '''resblockPosition(.+)'''  # Longitude, Latitude
    items = re.search(regex, results)
    content = items.group()[:-1]
    position = content.split(':')[1]
    coordination = position[1:-1].split(",")
    try:
        field.extend(transCoordinateSystem.bd09_to_wgs84(float(coordination[0]), float(coordination[1])))
    except ValueError:
        write_log("{} has no coordination".format(lianjia_id))
        pass

    price = soup.find('div', {'class': 'price'})  # Price
    try:
        total_price = price.span.text
        unit_price = price.b.text
    except AttributeError:
        total_price = 'None'
        unit_price = 'None'
    field.extend([total_price, unit_price])

    contents = soup.find('div', {'class': 'msg'})  # Message of transaction
    for label in contents.findAll('label'):
        field.append(label.text)

    contents = soup.find('div', {'class': 'introContent'})
    for li in contents.findAll('li'):  # Basic information
        info = li.text.replace(li.span.text, '').replace(' ', '')
        if info is not None:
            field.append(info)
        else:
            field.append('None')

    data = dict(zip(list_key, field))
    sheet.insert_one(data)
    write_log("{} is done".format(lianjia_id))


def write_log(str):
    print(str)
    with open("log.log", 'a', encoding='utf-8') as f:
        f.write(str + '\n')


def save():
    """
    将数据库中的数据保存到txt文本文件
    :return:
    """
    f = open("cd_lianjia_info.txt", 'a', encoding='utf-8')
    f.write("lianjia_id\ttitle\tdeal_time\tlongitude\tlatitude\ttotal_price\t"
            "unit_price\tasking_price\ttrans_period\tprice_num\twatch_num\t"
            "focus_num\tclick_num\thouse_type\tfloor\tfloor_area\t"
            "house_structure\tinner_area\tbuilding_type\torientation\t"
            "built_year\tdecoration\tbuilding\theating\televator_ratio\t"
            "property_period\televator\tlianjia\tproperty_type\trelease_date\t"
            "use\ttwo_years\tshared_owner\n")

    for item in sheet.find({}):
        f.write("{lianjia_id}\t{title}\t{deal_time}\t{longitude}\t{latitude}\t{total_price}\t"
                "{unit_price}\t{asking_price}\t{trans_period}\t{price_num}\t{watch_num}\t"
                "{focus_num}\t{click_num}\t{house_type}\t{floor}\t{floor_area}\t"
                "{house_structure}\t{inner_area}\t{building_type}\t{orientation}\t"
                "{built_year}\t{decoration}\t{building}\t{heating}\t{elevator_ratio}\t"
                "{property_period}\t{elevator}\t{lianjia}\t{property_type}\t{release_date}\t"
                "{use}\t{two_years}\t{shared_owner}\n".format(**item))
    f.close()


def main():
    # f = open("cd_lianjia_list.txt", 'r', encoding='utf-8')
    # lines = f.read()
    # for line in lines.split("\n"):
    #     word = line.split('\t')
    #     name = word[0].strip()
    #     uid = word[1].strip()  # word[1]是小区的uid号
    #     if len([i for i in sheet_list.find({"uid": uid})]):
    #         pass
    #     else:
    #         get_url_list(name, uid)
    # print('All lianjia_ids were collected.')

    for url_list in sheet_list.find({}):
        lianjia_ids = url_list['url_list'].split(',')
        for lianjia_id in lianjia_ids:
            if len([i for i in sheet.find({"lianjia_id": lianjia_id})]):
                pass
            else:
                get_info(lianjia_id)

    save()


if __name__ == '__main__':
    main()
