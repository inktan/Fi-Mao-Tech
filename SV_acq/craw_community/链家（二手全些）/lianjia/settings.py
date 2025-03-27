#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "Yong"


from pymongo import MongoClient

client = MongoClient(host='localhost', port=27017, connect=False)
db = client['lianjia']
sheet = db['lianjia_cd']
sheet_list = db['lianjia_cd_list']
