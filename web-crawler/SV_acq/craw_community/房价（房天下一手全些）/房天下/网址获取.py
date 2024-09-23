# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 10:42:19 2018

@author: Administrator
"""

import requests
from bs4 import BeautifulSoup

# 新小区
# 所有的小区网址爬取
resident_list = []
with open('E://xusha/competation/new_community/南京周边.txt', 'w') as f:
    for i in range(1, 4):
        page_r = requests.get('http://esf.nanjing.fang.com/housing/13046__1_0_0_0_' + str(i) + '_0_0_0/')
        page_r.encoding = 'gb2312'
        soup = BeautifulSoup(page_r.text, "lxml")

        a = soup.select('.houseList')[0]
        b = a.select('div > dl > dt > a')

        for each in b:
            href = each['href']
            resident_list.append(href)
            f.write(href)
            f.write('\n')
       
