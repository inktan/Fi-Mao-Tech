#!/usr/bin/python
#-*- coding:utf-8 -*-
import time
import urllib2
import string
import sys,os
from bs4 import BeautifulSoup
import re
import codecs

def getlist(html):
    soup = BeautifulSoup(html,fromEncoding="utf-8")
    dds = soup.findAll('div',{'class':'info'})
    lianjia_list = ''
    for dd in dds:
        title = dd.find('div',{'class':'title'})
        name = title.getText()
        href = title.a.get("href").replace("https://cd.lianjia.com/xiaoqu/","").replace("/","")
        lianjia_list += "%s\t%s\n" % (name, href)
    outdata = codecs.open(r'E:\Python\Crawler-master\LianJia\LianJia\Yong\cd_lianjia_list.txt',"a")
    outdata.write("%s" % lianjia_list)
    outdata.close()

def getHtml(url):
    headers={'User-Agent':'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)'}
    opener = urllib2.build_opener()
    request = urllib2.Request(url,headers=headers)
    page = opener.open(request)
    data = page.read()
    return data

def getLianjia_List():
##chengdu
    regions = ['jinjiang','qingyang','wuhou','gaoxin7','chenghua','jinniu','tianfuxinqu',
    'gaoxinxi1','shuangliu','wenjiang','pidou','longquanyi','xindou']
    pages = (39,58,54,25,34,57,10,3,18,17,20,16,21)

    for i in range(0,13,1):
        for j in range(1,pages[i],1):
            url_tmp = r"https://cd.lianjia.com/xiaoqu/"+str(regions[i])+"/pg"+str(j)+"/"
            tags_html = getHtml(url_tmp)
            getlist(tags_html)
            print("Region %s Page %s is done" %((regions[i]), str(j)))
            time.sleep(1)

if __name__ == '__main__':
    getLianjia_List()