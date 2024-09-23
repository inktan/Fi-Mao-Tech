# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 11:09:12 2018

@author: Administrator
"""

import requests
from bs4 import BeautifulSoup

with open('E://xusha/competation/new_community/鼓楼.txt', 'r') as f:
    website_list = f.readlines()
    with open('E://xusha/competation/new_community/鼓楼1.csv', 'w', encoding='gb2312') as fw:
        count = 1
        for each in website_list:
            
            info_r = requests.get(each[:-1])
            info_r.encoding = 'gb2312'
            soup = BeautifulSoup(info_r.text, "lxml")
            
            # name of resident
            name= soup.select("h1")[0].text
            
            # num of households
            
            
            try:
                households = soup.select('.Rinfolist')[0]
                if '房屋总数' in households.select('ul > li')[4].text:
                    households = households.select('ul > li')[4].text[4:-1]
                elif '房屋总数' in households.select('ul > li')[2].text:
                    households = households.select('ul > li')[2].text[4:-1]
                elif '房屋总数' in households.select('ul > li')[3].text:
                    households = households.select('ul > li')[3].text[4:-1]
                elif '房屋总数' in households.select('ul > li')[5].text:
                    households = households.select('ul > li')[5].text[4:-1]
                elif '房屋总数' in households.select('ul > li')[6].text:
                    households = households.select('ul > li')[6].text[4:-1]
                elif '房屋总数' in households.select('ul > li')[7].text:
                    households = households.select('ul > li')[7].text[4:-1]
                fw.write(name + ',' + households + '\n')
            except BaseException:
                try:
                    fw.write(name + '\n')
                except BaseException:
                    fw.write(str(count) + '\n')

            print(count)
            count += 1