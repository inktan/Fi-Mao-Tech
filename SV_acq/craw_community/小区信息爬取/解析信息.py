# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 11:09:12 2018

@author: Administrator
"""

import requests
from bs4 import BeautifulSoup
import json
import time

with open('D://360data/重要数据/桌面/生活圈/爬小区信息/a.txt', 'r') as f:
    website_list = f.readlines()
    with open('D://360data/重要数据/桌面/生活圈/爬小区信息/10.csv', 'w', encoding='gb2312') as fw:
        count = 0
        for each in website_list:
            time.sleep(1)
            print(each[2:-2])
            info_r = requests.get('http://' + each[2:-2])
            info_r.encoding = 'gb2312'
            soup = BeautifulSoup(info_r.text, "lxml")
#            info_r_area = requests.get(each[:-1]+'xiangqing/')
#            info_r_area.encoding = 'gb2312'
#            soup_area = BeautifulSoup(info_r_area.text, 'lxml')
            try:
#                area = soup_area.select('dd')
#                area_write = ''
#                zhandiarea_write = ''
#                for each_dd in area:
#                    if '建筑面积' in each_dd.text:
#                        area_write = each_dd.text[5:-3]
##                        print(area_write)
#                    if '占地面积' in each_dd.text:
#                        zhandiarea_write = each_dd.text[5:-3]
                name= soup.select("h1")[0].text.strip()
                name = name.split('\n')[0]
                info_r = requests.get('http://apis.map.qq.com/ws/place/v1/suggestion/?region=南通市&keyword=' + name + '&key=KD5BZ-6ONR6-AW2SP-MYEOG-HSEFT-PVB4W')
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
