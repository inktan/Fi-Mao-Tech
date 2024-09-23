# 2-Data Collection-Web Crawling-2
# Add function of turning pages
# coding=utf-8
import urllib2
import time
from bs4 import BeautifulSoup

houseList = []

baseURL = 'http://bj.58.com/chuzu/pn'

for i in range(1,4):

    data = urllib2.urlopen(baseURL + str(i))
    data = data.read()
    time.sleep(2)

    soup = BeautifulSoup(data, 'html5lib', from_encoding='utf8')
    table = soup.findAll('ul','listUl')
    table = table[0]
    contents = table.findAll('li')

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

    print str(len(houseList)) + ' pieces collected'


output = open('houseList2.txt', 'w')
for house in houseList:
    print house[0]
    info = house[0]+';'+house[1]+';'+house[2]+';'+house[3]+';'+'\n'
    output.write(info.encode('utf-8'))

output.close()