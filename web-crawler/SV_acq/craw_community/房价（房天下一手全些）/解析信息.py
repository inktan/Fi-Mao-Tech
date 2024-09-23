# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 11:09:12 2018

@author: Administrator
"""

import requests
from bs4 import BeautifulSoup
import json
import time

with open('E://xusha/competation/new_community/江宁.txt', 'r') as f:
    website_list = f.readlines()
    with open('E://xusha/competation/new_community/江宁.csv', 'w', encoding='gb2312') as fw:
        count = 1
        for each in website_list:
            time.sleep(1)
            info_r = requests.get(each[:-1])
            info_r.encoding = 'gb2312'
            soup = BeautifulSoup(info_r.text, "lxml")

            try:
                name= soup.select("h1")[0].text
                info_r = requests.get('http://apis.map.qq.com/ws/place/v1/suggestion/?region=南京市江宁区&keyword=' + name + '&key=FY5BZ-NCLWP-REDDA-LAH6F-IKYOV-EWFA4')
                temp = json.loads(info_r.text)
                info_list = temp['data'][0]
                lng = info_list['location']['lng']
                lat = info_list['location']['lat']
            
                households = ''
                houseinfo = soup.select('.Rinfolist')[0]
                houseyear = ""
                housetype = ""
#                print(houseinfo.select('li'))
                for each in houseinfo.select('li'):
                    if '房屋总数' in each.text:
                        households = each.text[4:-1]
                    if '建筑年代' in each.text:
                        houseyear = each.text[4:]
                        houseyear.replace('，', ' ')
                        houseyear.replace(',', ' ')
                    if '建筑类型' in each.text:
                        housetype = each.text[4:]
                        if "板楼" in housetype and "塔楼" in housetype:
                            housetype = "板塔结合"
#                    print(1)
                houseprice = soup.select('.prib')[0].text
                fw.write(name + ',' + households + ',' + str(lng) + ',' + str(lat) + ',' + houseprice + ',' + houseyear + ',' + housetype + '\n')
                time.sleep(0.5)
            except BaseException:
                try:
                    fw.write(name + '\n')
                except BaseException:
                    fw.write(str(count) + '\n')

            print(count)
            count += 1
