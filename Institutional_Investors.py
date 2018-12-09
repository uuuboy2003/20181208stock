#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 19:11:30 2018

@author: cheating
"""
#繪圖用
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import requests
import datetime
from io import StringIO
import pandas as pd

    
###############################################################################
#                              股票機器人 籌碼面分析                            #
###############################################################################

# 畫出籌碼面圖
def stockII(stocknumber):
    
    sumstock=[]
    stockdate=[]
    for i in range(11,0,-1):
        date = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=i),'%Y%m%d') #先設定要爬的時間
        r = requests.get('http://www.twse.com.tw/fund/T86?response=csv&date='+date+'&selectType=ALLBUT0999') #要爬的網站
        if r.text != '\r\n': #有可能會沒有爬到東西，有可能是六日
            get = pd.read_csv(StringIO(r.text), header=1).dropna(how='all', axis=1).dropna(how='any') # 把交易所的csv資料載下來
            get=get[get['證券代號']==stocknumber] # 找到我們要搜尋的股票
            if len(get) >0:
                get['三大法人買賣超股數'] = get['三大法人買賣超股數'].str.replace(',','').astype(float) # 去掉','這個符號把它轉成數字
                stockdate.append(date)
                sumstock.append(get['三大法人買賣超股數'].values[0])
    if len(stockdate) >0:
        positive=0
        negative=0
        
        for j in sumstock:
            if j >= 0:
                positive +=1
            else:
                negative +=1
        return stocknumber + '在這' + str(len(sumstock)) + '天中，' + str(positive) + '天買進，' + str(negative) + '天賣出。'
    