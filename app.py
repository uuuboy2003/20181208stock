
import requests
import datetime
from bs4 import BeautifulSoup
from flask import Flask, request, abort	
from linebot import (LineBotApi, WebhookHandler, exceptions)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import mongodb
import re
import json
import mongodb
import Fundamental_Analysis
import Institutional_Investors
#import Technical_Analysis

app = Flask(__name__)


# Channel Access Token
line_bot_api = LineBotApi('tJpXyrfmGqGfGU6XYLBa1rSsFHAixTsXwXutIJUkc9CD1Fl6tG04NCQGYKMozCekwHeGKe9tcYE78bSg6gAHb/sxwTGZezAw+V7R5S9flWPCWbAt86KVGEWJH/opS/dA7br3tiB0Bj7igJEBM2rQXgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('44ce2178494117be6594101fdf1e96c2')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):  
    ### 抓到顧客的資料 ###
    profile = line_bot_api.get_profile(event.source.user_id)
    nameid = profile.display_name #使用者名稱
    uid = profile.user_id #使用者ID
    
    ### 如果這個使用者沒有紀錄的話，就記錄他 ###
    if mongodb.show_user(uid):
        mongodb.write_user(nameid,uid)
    
    ### 把使用者的資料儲存下來 ###
    usespeak=str(event.message.text) #使用者講的話
   
#####################################系統功能按鈕##############################

    if re.match('[0-9]{4}[<>][0-9]',usespeak): # 先判斷是否是使用者要用來存股票的
        mongodb.write_user_stock_fountion(stock=usespeak[0:4], bs=usespeak[4:5], price=usespeak[5:])
        line_bot_api.push_message(uid, TextSendMessage(usespeak[0:4]+'已經儲存成功'))
        return 0


    elif re.match('刪除[0-9]{4}',usespeak): # 刪除存在資料庫裡面的股票
        mongodb.delete_user_stock_fountion(stock=usespeak[2:])
        line_bot_api.push_message(uid, TextSendMessage(usespeak+'已經刪除成功'))
        return 0
        
        
    elif re.match('[0-9]{4}',usespeak): # 如果只有給四個數字就判斷是股票查詢
        mongodb.update_temporary_stock(uid,usespeak)
        url = 'https://tw.stock.yahoo.com/q/q?s=' + usespeak 
        #請求網站
        list_req = requests.get(url)
        #將整個網站的程式碼爬下來
        soup = BeautifulSoup(list_req.content, "html.parser")
        #找到b這個標籤
        getstock= soup.findAll('b')[1].text #抓到收盤價格
        line_bot_api.push_message(uid, TextSendMessage(usespeak + '目前的價格是' + getstock))
        return 0
    
    elif re.match('我的股票',usespeak):  # 秀出所有自動推撥的股票
        
        get=mongodb.show_user_stock_fountion()
        msg=''

        if len(get) >0:
            for i in get:  
                msg += i['stock'] + " " + i['bs'] + " " + str(i['price']) +'\n'
            line_bot_api.push_message(uid, TextSendMessage(msg))
            return 0
        else:
            line_bot_api.push_message(uid, TextSendMessage('沒有資料'))
            return 0
        

    elif re.match('籌碼面分析',usespeak): 
        usespeak=mongodb.cache_temporary_stock(uid)
        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
        # 推撥籌碼面分析
        line_bot_api.push_message(uid, TextSendMessage(Institutional_Investors.stockII(usespeak)))
        return 0
#    
#    elif re.match('KD圖',usespeak): 
#        usespeak=mongodb.cache_temporary_stock(uid)
#        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
#        # 推撥KD
#        line_bot_api.push_message(uid, TextSendMessage(Technical_Analysis.stock_KD(usespeak)))
#        return 0
#    
#    elif re.match('MA圖',usespeak): 
#        usespeak=mongodb.cache_temporary_stock(uid)
#        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
#        # 推撥MA
#        line_bot_api.push_message(uid, TextSendMessage(Technical_Analysis.stock_MA(usespeak)))
#        return 0
#    
#    elif re.match('MACD圖',usespeak): 
#        usespeak=mongodb.cache_temporary_stock(uid)
#        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
#        # 推撥MACD
#        line_bot_api.push_message(uid, TextSendMessage(Technical_Analysis.stock_MACD(usespeak)))
#        return 0
#    
#    elif re.match('OBV圖',usespeak): 
#        usespeak=mongodb.cache_temporary_stock(uid)
#        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
#        # 推撥OBV
#        line_bot_api.push_message(uid, TextSendMessage(Technical_Analysis.stock_OBV(usespeak)))
#        return 0
#    
#    elif re.match('威廉圖',usespeak): 
#        usespeak=mongodb.cache_temporary_stock(uid)
#        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
#        # 推撥威廉
#        line_bot_api.push_message(uid, TextSendMessage(Technical_Analysis.stock_William(usespeak)))
#        return 0
#    
#    elif re.match('ATR圖',usespeak): 
#        usespeak=mongodb.cache_temporary_stock(uid)
#        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
#        # 推撥ATR
#        line_bot_api.push_message(uid, TextSendMessage(Technical_Analysis.stock_ATR(usespeak)))
#        return 0
#    
#    elif re.match('ADX圖',usespeak): 
#        usespeak=mongodb.cache_temporary_stock(uid)
#        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
#        # 推撥ADX
#        line_bot_api.push_message(uid, TextSendMessage(Technical_Analysis.stock_ADX(usespeak)))
#        return 0
#    
#    elif re.match('RSI圖',usespeak): 
#        usespeak=mongodb.cache_temporary_stock(uid)
#        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
#        # 推撥RSI
#        line_bot_api.push_message(uid, TextSendMessage(Technical_Analysis.stock_RSI(usespeak)))
#        return 0
#    
#    elif re.match('MFI圖',usespeak): 
#        usespeak=mongodb.cache_temporary_stock(uid)
#        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
#        # 推撥MFI
#        line_bot_api.push_message(uid, TextSendMessage(Technical_Analysis.stock_MFI(usespeak)))
#        return 0
#    
#    elif re.match('ROC圖',usespeak): 
#        usespeak=mongodb.cache_temporary_stock(uid)
#        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
#        # 推撥ROC
#        line_bot_api.push_message(uid, TextSendMessage(Technical_Analysis.stock_ROC(usespeak)))
#        return 0
    elif re.match('毛利率大於90％',usespeak): 
        usespeak=mongodb.cache_temporary_stock(uid)
        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
        # 推撥毛利率大於90％
        line_bot_api.push_message(uid,TextSendMessage('毛利率大於90％的股票：\n'+Fundamental_Analysis.gpm()))
        return 0
    
    elif re.match('每股淨值大於100',usespeak): 
        usespeak=mongodb.cache_temporary_stock(uid)
        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
        # 推撥每股淨值大於100
        line_bot_api.push_message(uid,TextSendMessage('每股淨值大於100的股票：\n'+Fundamental_Analysis.pbr()))
        return 0
    
    elif re.match('每股盈餘大於5',usespeak): 
        usespeak=mongodb.cache_temporary_stock(uid)
        line_bot_api.push_message(uid, TextSendMessage('稍等一下, 雲端運算中...'))
        # 推撥每股盈餘大於5
        line_bot_api.push_message(uid,TextSendMessage('每股盈餘大於5的股票：\n'+Fundamental_Analysis.eps()))
        return 0
    # 傳送多重按鈕介面訊息
    elif re.match('技術面分析',usespeak):
        message = TemplateSendMessage(
            alt_text='技術面分析（Technical Analysis）',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/7FwK6MA.png',
                        title='技術面分析',
                        text='Technical Analysis',
                        actions=[
                            MessageTemplateAction(
                                label='ROC圖',
                                text='ROC圖'
                            ),
                            MessageTemplateAction(
                                label='MA圖',
                                text='MA圖'
                            ),
                            MessageTemplateAction(
                                label='MACD圖',
                                text='MACD圖'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://imgur.com/9BlDjoF.png',
                        title='技術面分析',
                        text='Technical Analysis',
                        actions=[
                            MessageTemplateAction(
                                label='OBV圖',
                                text='OBV圖'
                            ),
                            MessageTemplateAction(
                                label='威廉圖',
                                text='威廉圖'
                            ),
                            MessageTemplateAction(
                                label='ATR圖',
                                text='ATR圖'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://imgur.com/OkpeEZ7.png',
                        title='技術面分析',
                        text='Technical Analysis',
                        actions=[
                            MessageTemplateAction(
                                label='ADX圖',
                                text='ADX圖'
                            ),
                            MessageTemplateAction(
                                label='RSI圖',
                                text='RSI圖'
                            ),
                            MessageTemplateAction(
                                label='MFI圖',
                                text='MFI圖'
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.push_message(uid, message)
        return 0
    elif re.match('基本面分析',usespeak): 
        buttons_template = TemplateSendMessage(
            alt_text='基本面分析',
            template=ButtonsTemplate(
                title='基本面分析（Fundamental Analysis）',
                text='請選擇',
                actions=[
                    MessageTemplateAction(
                        label='毛利率大於90％',
                        text='毛利率大於90％'
                    ),
                    MessageTemplateAction(
                        label='每股淨值大於100',
                        text='每股淨值大於100'
                    ),
                    MessageTemplateAction(
                        label='每股盈餘大於5',
                        text='每股盈餘大於5'
                    ),
                    
                ]
            )
        )
        line_bot_api.push_message(uid, buttons_template)
        return 0
        
    else: # 都找不到就回答看不懂
        line_bot_api.push_message(uid,message)
        return 0
            
                    

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 27017))
    app.run(host='0.0.0.0', port=port)

