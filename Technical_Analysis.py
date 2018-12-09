# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 17:29:13 2018

@author: cheating
"""
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
from pandas_datareader import data
import fix_yahoo_finance as yf # yahoo專用的拿來拉股票資訊
import datetime
import talib #技術分析專用
import matplotlib.pyplot as plt # 繪圖專用
import mpl_finance as mpf # 專門用來畫蠟燭圖的
import pylab as pl  # 讓圖片的文字可以旋轉

###############################################################################
#                              股票機器人 技術面分析                            #
###############################################################################

def TheConstructor(userstock):
    # 設定要的資料時間
    start = datetime.datetime.now() - datetime.timedelta(days=365) #先設定要爬的時間
    end = datetime.date.today()
    
    # 與yahoo請求
    pd.core.common.is_list_like = pd.api.types.is_list_like
    yf.pdr_override()
    
    # 取得股票資料
    stock = data.get_data_yahoo(userstock+'.TW', start, end)
    return stock


#---------------------------------------- KD指標 ------------------------------------
def stock_KD(userstock):
    
    stock=TheConstructor(userstock)
    
    ret = pd.DataFrame(list(talib.STOCH(stock['High'].values, stock['Low'].values, stock['Close'].values))).transpose()
    ret.columns=['K','D']
    ret.index = stock['Close'].index
    if ret.iloc[len(ret)-1]['K'] > ret.iloc[len(ret)-1]['D']:
        return 'K朝上，可買進'
    else:
        return 'K朝下，請三思'
#-------------------------------- 移動平均線（Moving Average）------------------------------------
def stock_MA(userstock):
    stock=TheConstructor(userstock)
    
    ret = pd.DataFrame(talib.SMA(stock['Close'].values,10), columns= ['10-day average']) #10日移動平均線
    ret = pd.concat([ret,pd.DataFrame(talib.SMA(stock['Close'].values,20), columns= ['20-day average'])], axis=1) #10日移動平均線
    ret = pd.concat([ret,pd.DataFrame(talib.SMA(stock['Close'].values,60), columns= ['60-day average'])], axis=1) #10日移動平均線
    ret = ret.set_index(stock['Close'].index.values)
    
    if ret.iloc[len(ret)-1]['10-day average'] > ret.iloc[len(ret)-1]['60-day average']:
        return '短期線突破長期線，可買進'
    else:
        return '短期線跌破長期線，請三思'
#-------------------- 指數平滑異同移動平均線（Moving Average Convergence / Divergence）------------------------------------
def stock_MACD(userstock):
    stock=TheConstructor(userstock)
    ret=pd.DataFrame()
    ret['MACD'],ret['MACDsignal'],ret['MACDhist'] = talib.MACD(stock['Close'].values,fastperiod=6, slowperiod=12, signalperiod=9)
    ret = ret.set_index(stock['Close'].index.values)
    
    if ret.iloc[len(ret)-1]['MACD'] > ret.iloc[len(ret)-1]['MACDsignal']:
        return '短期線突破長期線，可買進'
    else:
        return '短期線跌破長期線，請三思'
#------------------------ 能量潮指標（On Balance Volume）------------------------------------
def stock_OBV(userstock):
    stock=TheConstructor(userstock)
    ret = pd.DataFrame(talib.OBV(stock['Close'].values, stock['Volume'].values.astype(float)), columns= ['OBV'])
    ret = ret.set_index(stock['Close'].index.values)
    
    if ret.iloc[len(ret)-1]['OBV'] > ret.iloc[len(ret)-2]['OBV']:
        return 'OBV向上'
    else:
        return 'OBV向上向下'
#------------------------ 威廉指數（Williams Overbought）------------------------------------
def stock_William(userstock):
    stock=TheConstructor(userstock)
    ret = pd.DataFrame(talib.WILLR(stock['High'].values, stock['Low'].values, stock['Open'].values), columns= ['Williams'])
    ret = ret.set_index(stock['Close'].index.values)

    if ret.iloc[len(ret)-1]['Williams'] > -20:
        return '威廉指數表示，買進'
    elif  ret.iloc[len(ret)-1]['Williams'] < -80:
        return '威廉指數表示，賣出'
    else:
        return '不動作'
#------------------------ 平均真實區域指標（Average True Range）------------------------------------
def stock_ATR(userstock):
    stock=TheConstructor(userstock)
    ret = pd.DataFrame(talib.ATR(stock['High'].values, stock['Low'].values, stock['Close'].values), columns= ['Average True Range'])
    ret = ret.set_index(stock['Close'].index.values)
    
    if ret.iloc[len(ret)-1]['Average True Range'] > 0.8:
        return '波動極大'
    else:
        return '微服震動'
#------------------------ 平均趨向指標（Average Directional Indicator）------------------------------------
def stock_ADX(userstock):
    stock=TheConstructor(userstock)
    ret = pd.DataFrame(talib.ADX(stock['High'].values, stock['Low'].values, stock['Close'].values), columns= ['Average True Range'])
    ret = ret.set_index(stock['Close'].index.values)    
    
    if ret.iloc[len(ret)-1]['Average True Range'] > ret.iloc[len(ret)-2]['Average True Range']:
        return '能量向上'
    else:
        return '能量衰減'
#------------------------ 相對強弱指數（Relative Strength Index）------------------------------------
def stock_RSI(userstock):
    stock=TheConstructor(userstock)
    # RSI的天數設定一般是6, 12, 24
    ret = pd.DataFrame(talib.RSI(stock['Close'].values,24), columns= ['Relative Strength Index'])
    ret = ret.set_index(stock['Close'].index.values)
    
    if ret.iloc[len(ret)-1]['Relative Strength Index'] > 50:
        return '強勢'
    else:
        return '弱勢'
#------------------------ 資金流動指標（Money Flow Index）------------------------------------
def stock_MFI(userstock):
    stock=TheConstructor(userstock)
    ret = pd.DataFrame(talib.MFI(stock['High'].values,stock['Low'].values,stock['Close'].values,stock['Volume'].values.astype(float), timeperiod=14), columns= ['Money Flow Index'])
    ret = ret.set_index(stock['Close'].index.values)

    if ret.iloc[len(ret)-1]['Money Flow Index'] > 50:
        return '強勢'
    else:
        return '弱勢'
#------------ 接收者操作特徵曲線（Receiver Operating Characteristic Curve）------------------------------------
def stock_ROC(userstock):
    stock=TheConstructor(userstock)
    ret = pd.DataFrame(talib.ROC(stock['Close'].values, timeperiod=10), columns= ['Receiver Operating Characteristic curve'])
    ret = ret.set_index(stock['Close'].index.values)
    
    if ret.iloc[len(ret)-1]['Receiver Operating Characteristic curve'] > ret.iloc[len(ret)-2]['Receiver Operating Characteristic curve'] and ret.iloc[len(ret)-1]['Receiver Operating Characteristic curve'] >0:
        return '強勢，可買進'
    elif  ret.iloc[len(ret)-1]['Receiver Operating Characteristic curve'] < ret.iloc[len(ret)-2]['Receiver Operating Characteristic curve'] and ret.iloc[len(ret)-1]['Receiver Operating Characteristic curve'] <0:
        return '弱勢，要出場'
    else:
        return '沒有特別操作'