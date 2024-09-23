# 2-Data Collection-Web Crawling-3
# Get detailed info from each url individually
# coding=utf-8
import urllib2
import time
from bs4 import BeautifulSoup
import random

houseList = []

url = 'http://bj.58.com/chuzu/pn1'

data = urllib2.urlopen(url)
data = data.read()
time.sleep(2)

soup = BeautifulSoup(data, 'html5lib', from_encoding='utf8')
table = soup.findAll('ul','listUl')
table = table[0]
contents = table.findAll('li')

urlList = []

for item in contents:
    try:
        url = item.h2.a['href'].strip()
        urlList.append(url)
    except:
        continue

print str(len(urlList)) + ' pieces collected'

for testurl in urlList:
    try:
        detaildata = urllib2.urlopen(testurl)
        detaildata = detaildata.read()
        time.sleep(random.randint(1,4))

        detailsoup = BeautifulSoup(detaildata, 'html5lib', from_encoding='utf8')

        detail = detailsoup.find('div','house-basic-info')

        price = detail.find('b','f36').text
        infos = detail.find('ul','f14').findAll('li')

        rentType = infos[0].text.strip()
        size = infos[1].text.replace(' ','').strip()
        facing = infos[2].text.strip()
        community = infos[3].a.text
        region = infos[4].a.text
        address = infos[5].findAll('span')[1].text.strip()

        coordScript = detailsoup.findAll('script')
        start = coordScript[0].text.find('lat')
        end = coordScript[0].text.find('baidulat')

        coord = coordScript[0].text[start:end]
        lat = coord.split(',')[0][6:-1]
        lon = coord.split(',')[1][7:-1]

        houseList.append([price,rentType,size,facing,community,region,address,lat,lon])
        print 'collecting......' + community
    except:
        print testurl + '----------error'

output = open('houseList3_0802.txt', 'w')
for house in houseList:
    print house[3]
    info = ';'.join(house)+'\n'
    output.write(info.encode('utf-8'))

output.close()