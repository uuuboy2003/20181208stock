#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 09:33:35 2018

@author: cheating
"""
import requests
import pandas as pd
import numpy as np
import datetime

def financial_statement(type='資產負債表'):
    
    # 決定要抓什麼時候的報表
    today = datetime.date.today() # 今天的時間
    year=today.year # 預設年是今年
    if today.month >11:
        season=3
    elif today.month >8:
        season=2
    elif today.month >5:
        season=1
    else:
        year -= 1
        season=4
    year =year-1911 # 必須要是民國年
    
    if type == '綜合損益表':
        url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb04'
    elif type == '資產負債表':
        url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb05'
    elif type == '營益分析表':
        url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb06'
    else:
        print('type does not match')
    r = requests.post(url, {
        'encodeURIComponent':1,
        'step':1,
        'firstin':1,
        'off':1,
        'TYPEK':'sii',
        'year':str(year),
        'season':str(season),
    })
    
    r.encoding = 'utf8'
    dfs = pd.read_html(r.text)
    
    
    for i, df in enumerate(dfs):
        df.columns = df.iloc[0] # 把欄位名稱丟進去
        dfs[i] = df.iloc[1:] # 
        
    df = pd.concat(dfs).applymap(lambda x: x if x != '--' else np.nan)
    df = df[df['公司代號'] != '公司代號']
    df = df[~df['公司代號'].isnull()]
    
    return df

# 毛利率篩選
def gpm():
    df=financial_statement(type='營益分析表')
    return '\n'.join(df[pd.to_numeric(df['毛利率(%)(營業毛利)/(營業收入)'])>90]['公司代號'])

# 每股淨值篩選
def pbr():
    df=financial_statement(type='資產負債表')
    return '\n'.join(df[pd.to_numeric(df['每股參考淨值'])>100]['公司代號'])

# 每股盈餘篩選
def eps():
    df=financial_statement(type='綜合損益表')
    return '\n'.join(df[pd.to_numeric(df['基本每股盈餘（元）'])>5]['公司代號'])