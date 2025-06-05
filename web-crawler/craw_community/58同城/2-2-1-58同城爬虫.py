# -*- coding: utf-8 -*-
# 2-Data Collection-Web Crawling-1
# Basic crawler for 58.com
# coding=utf-8
import urllib2
import time
from bs4 import BeautifulSoup

houseList = []

url = 'http://bj.58.com/chuzu/pn1/'

data = urllib2.urlopen(url)
data = data.read()
time.sleep(2)

soup = BeautifulSoup(data, 'html5lib', from_encoding='utf-8')

table = soup.findAll('ul','listUl')

table = table[0]
contents = table.findAll('li')
len(contents)

for item in contents:
    try:
        title = item.findAll('h2')[0].text.strip()
    except:
        title = ''
    try:
        size = item.find('p', 'room').text
    except:
        size = ''
    try:
        region = item.find('p', 'add').find('a').text
    except:
        region = ''
    try:
        price = item.find('div','money').text.strip()
    except:
        price = ''

    houseList.append([title,size,region,price])


output = open('houseList.txt', 'w')
for house in houseList:
    print house[0]
    info = house[0]+';'+house[1]+';'+house[2]+';'+house[3]+'\n'
    output.write(info.encode('utf-8'))

output.close()