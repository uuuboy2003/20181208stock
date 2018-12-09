#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 20:10:16 2018

@author: cheating
"""

from pymongo import MongoClient
import urllib.parse
import datetime

##### 資料庫設定 #####
host = 'ds019893.mlab.com' #主機位置
port = '19893' #port號碼
username = urllib.parse.quote_plus('hello_1') #使用者帳號
password = urllib.parse.quote_plus('Poppppoppp1234') #使用者密碼
# Authentication Database認證資料庫
Authdb='20181209stock'

###############################################################################
#                           LineBot股票機器人mongoDB#                            #
###############################################################################

#資料庫連接
def constructor():
    client = MongoClient('mongodb://%s:%s@%s:%s/%s?authMechanism=SCRAM-SHA-1'
                      % (username, password, host, port, Authdb))
    db = client[Authdb]
    return db

#----------------------------抓取使用者--------------------------
def show_user(uid):  
    db=constructor()
    collect = db['member']
    cel=list(collect.find())
    
    ans=True
    for i in cel:
        if uid == i['uid']:
            ans = False
    return ans

#----------------------------儲存使用者--------------------------
def write_user(nameid, uid):  
    db=constructor()
    collect = db['member']
    collect.insert({"nameid": nameid,
                    "uid": uid,
                    "temporary_stock": '2002',
                    "date_info": datetime.datetime.utcnow()
                    })
    
#----------------------------儲存使用者的股票--------------------------
def write_user_stock_fountion(stock, bs, price):  
    db=constructor()
    collect = db['mystock']
    collect.insert({"stock": stock,
                    "data": 'care_stock',
                    "bs": bs,
                    "price": float(price),
                    "date_info": datetime.datetime.utcnow()
                    })
    
#----------------------------殺掉使用者的股票--------------------------
def delete_user_stock_fountion(stock):  
    db=constructor()
    collect = db['mystock']
    collect.remove({"stock": stock})
    
#----------------------------抓取使用者的股票--------------------------
def show_user_stock_fountion():  
    db=constructor()
    collect = db['mystock']
    cel=list(collect.find({"data": 'care_stock'}))

    return cel

#----------------------------抓暫存的股票名稱--------------------------
def cache_temporary_stock(uid):  
    db=constructor()
    collect = db['member']
    cel=list(collect.find({"uid": uid}))

    return cel[0]['temporary_stock']

#----------------------------存取暫存的股票名稱--------------------------
def update_temporary_stock(uid,stock):
    db=constructor()
    collect = db['member']
    collect.update({ "userid": uid }, {'$set': {'temporary_stock':stock}})
    
    