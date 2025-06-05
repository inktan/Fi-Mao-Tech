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
with open('H://Users/沙/Desktop/生活圈/爬小区信息/a.txt', 'w') as f:
    for i in range(1, 101):
        print(i)
        page_r = requests.get('http://nt.esf.fang.com/housing/__1_0_0_0_'+str(i)+'_0_0_0/')
        page_r.encoding = 'gb2312'
        soup = BeautifulSoup(page_r.text, "lxml")

        a = soup.select('.houseList')[0]
        b = a.select('div > dl > dt > a')

        for each in b:
            href = each['href']
            resident_list.append(href)
            f.write(href)
            f.write('\n')
       
