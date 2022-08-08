from datetime import datetime ; import time ; import schedule
import pyupbit ; import requests; import pandas as pd
from os import system ; from collections import defaultdict
import random
from slack_msg import * ; from DMLfunc import *
from get_orderd_ticker import *

# access키와 secret키 입력
access = ""
secret = ""
upbit = pyupbit.Upbit(access, secret)

LongStrategyCoin = ["KRW-IQ","KRW-SRM","KRW-SAND"] ; Forbidden_Coin = ['KRW-BTC', 'KRW-BTT', 'KRW-XEC']
total = 60000
left = 60000
# K값, 동시 구매 가능한 코인 개수
K_value = 0.3
Limit_Value = 10 ; buy_Persent = 0.1
Date_ID = 0 ; start_rank = 10

CoinInfo = defaultdict(dict)
CoinList = [] ; Coin_Target = {} ; Coin_MA15 = {}

#초기화
def initialize() :
    global CoinInfo

    temp = get_My_CoinList()
    temp_to_add = []

    for curCoin in temp :
        if not(curCoin in CoinInfo) :
            temp_to_add.append(curCoin)
            
    for curCoin in temp_to_add :
        CoinInfo[curCoin]["HighPrice"] = 0
        CoinInfo[curCoin]["BuyPrice"] = 0
        CoinInfo[curCoin]["StopLoss"] = -1
        CoinInfo[curCoin]["TimeProfit"] = -1
        CoinInfo[curCoin]["BuyTime"] = datetime.now()

    Set_CoinInfo()
    return True

#매수
def buy(coin, rate): 
    global CoinInfo
    global CoinList
    global left
    global NomoneyBool
    time.sleep(0.2)
    
    if left >= total * rate - 100:
        NomoneyBool = False
        upbit.buy_market_order(coin, total * rate)
        time.sleep(0.2)

        left -= total * rate
        
        message = coin + " buy " + str(total * rate) + "won "
        Prt_and_Slack(message)

        CoinList.remove(coin)
        Coin_Target.pop(coin) ; Coin_MA15.pop(coin)
    else :

        if NomoneyBool == False :
            message = "No Money"
            Prt_and_Slack(message)
        NomoneyBool = True

    return


# 매도
def sell(coin, currentprice): 
    global total
    global left
    global CoinInfo, Date_ID

    amount = get_balance(coin.split("-")[1])
    time.sleep(0.2)
    upbit.sell_market_order(coin, amount) 
    time.sleep(0.2)

    #수익 Output
    tempProfit = Calculate_Profit(CoinInfo[coin]["BuyPrice"],currentprice)*100
    Profit = format(tempProfit,'f')
    message = coin + " is all Sold. Profit: " + str(Profit) + "%"
    Prt_and_Slack(message)
    
    # 데이터 기록
    Connection_open('db.sqlite3')
    record_trade(Date_ID, coin, CoinInfo[coin]["BuyPrice"], currentprice, 
                            CoinInfo[coin]["BuyTime"], datetime.now())
    Connection_close('db.sqlite3')
    
    left += currentprice*amount
    total += (currentprice*amount - CoinInfo[coin]["BuyPrice"]*amount)

    return True

#수익 계산
def Calculate_Profit(buyprice, soldprice) :
    return (soldprice-buyprice)/buyprice

# 잔고 조회
def get_balance(currency):                          
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == currency:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

# 현재 가격 가져오기
def get_current_price(ticker):      
    result = pyupbit.get_current_price(ticker = ticker)  
    time.sleep(0.1) 
    return result

# 매수 평균가격 가져오기
def get_buy_avg_Price(ticker):
    result = upbit.get_avg_buy_price(ticker)
    time.sleep(0.1) 
    return result

# CoinInfo값들 설정
def Set_CoinInfo():
    global CoinInfo
    for curCoin in CoinInfo :
        curPrice = get_current_price(curCoin)

        if CoinInfo[curCoin]["HighPrice"] <= curPrice :
            CoinInfo[curCoin]["HighPrice"] = curPrice
        CoinInfo[curCoin]["BuyPrice"] = get_buy_avg_Price(curCoin)
        CoinInfo[curCoin]["StopLoss"] = CoinInfo[curCoin]["BuyPrice"]*0.8
        if CoinInfo[curCoin]["BuyPrice"]*1.02 < curPrice :
            CoinInfo[curCoin]["TimeProfit"] = (CoinInfo[curCoin]["HighPrice"] + CoinInfo[curCoin]["BuyPrice"])*0.5

        if curCoin in LongStrategyCoin :
            CoinInfo[curCoin]["TimeProfit"] = -1
            CoinInfo[curCoin]["StopLoss"] = -1
            if CoinInfo[curCoin]["BuyPrice"]*1.05 < curPrice :
                CoinInfo[curCoin]["TimeProfit"] = (CoinInfo[curCoin]["HighPrice"] + CoinInfo[curCoin]["BuyPrice"])*0.5
    return True

#현재 보유 중인 코인 목록 조회
def get_My_CoinList():
    temp = pd.DataFrame(upbit.get_balances()).iloc[:,0].values.tolist()
    time.sleep(0.3)
    result = []

    if "KRW" in temp :
        temp.remove("KRW")
    for cur in temp :
        result.append("KRW-" + cur)

    return result

# CoinList 초기화
def Get_CoinList_acc_trade() :
    global CoinList
    global CoinInfo
    global Coin_Target, Coin_MA15, Date_ID
        
    # 데이터 기록
    Connection_open('db.sqlite3')
    try:
        Date_ID = get_DateID_last()
    except:
        Date_ID = 0
    try:
        record_date(datetime.now().date())
        Date_ID = get_DateID_last()
        record_btc_eth(Date_ID, 'KRW-BTC', get_start_price('KRW-BTC'), get_ma15('KRW-BTC'))
        record_btc_eth(Date_ID, 'KRW-ETH', get_start_price('KRW-ETH'), get_ma15('KRW-ETH'))
    except Exception as e:
        message = "Error while INIT : " + str(e) 
        Prt_and_Slack(message)
    Connection_close('db.sqlite3')
    
    #sold_all_Coin()
    CoinList = [] ; Coin_Target = {} ; Coin_MA15 = {}
    CoinInfo = defaultdict(dict)

    
    templist = get_testcases(datetime.datetime.now() - timedelta(1), 'signedChangeRate', 0)

    temp = get_My_CoinList()

    CoinSet = set()

    for curCoin in templist:
        if (not(curCoin in temp) and not(curCoin in Forbidden_Coin)) :
            CoinSet.add(curCoin)
            Coin_Target[curCoin] = get_target_price(curCoin,"day", K_value)
            Coin_MA15[curCoin] = get_ma15(curCoin)
            if (len(CoinSet) >= Limit_Value) : break

    CoinList = list(CoinSet)

    message = "Today's Target : \n" + str(CoinList) 
    Prt_and_Slack(message)
    
    message = "balances : "+ str(left) 
    Prt_and_Slack(message)

    return 1

#15일 이동 평균선 조회
def get_ma15(ticker,interval = "day", count = 16):
    df = pyupbit.get_ohlcv(ticker, interval = interval, count = count + 1)
    time.sleep(0.1)
    ma15 = df['close'].rolling(count).mean().iloc[-2]
    return ma15

# 시작 가격 조회
def get_start_price(ticker, interval = "day"):             
    df = pyupbit.get_ohlcv(ticker, interval=interval, count=1)     
    time.sleep(0.1)
    start_price = df.iloc[0]['open']   
    return start_price


# 변동성 돌파 전략으로 매수 목표가 정하기 
def get_target_price(ticker, interval, k):        
    df = pyupbit.get_ohlcv(ticker, interval=interval, count=2)     
    time.sleep(0.1)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k       
    return target_price

# 보유중인 모든 코인 판매
def sold_all_Coin() :
    temp = get_My_CoinList()
    temp_to_delete = []
    
    for cur in LongStrategyCoin :
        if(cur in temp): temp_to_delete.append(cur)

    for cur in temp_to_delete :
        temp.remove(cur)

    for cur in temp :
        curPrice = get_current_price(cur)
        sell(cur, curPrice) 

# 프로그램 정상 실행 중인지 확인 
def check_running_right() :
    message = "Now Monitoring... " 
    Prt_and_Slack(message)



# 프로그램 작동
def run():
    schedule.every(3).hours.do(check_running_right)
    schedule.every().day.at("09:00:30").do(Get_CoinList_acc_trade)
    
    Get_CoinList_acc_trade()
    Prt_and_Slack("Start Program")
        
    while(True) :
        try:
            schedule.run_pending()
            
            #print(CoinList)

            for curCoin in CoinList :
                curPrice = get_current_price(curCoin)
                #print(curCoin, curPrice, Coin_MA15[curCoin], Coin_Target[curCoin])
                
                if curPrice > Coin_Target[curCoin] and curPrice > Coin_MA15[curCoin] :
                    buy(curCoin, buy_Persent)

            initialize()

            for curCoin in CoinInfo :
                curPrice = get_current_price(curCoin)
                
                if CoinInfo[curCoin]["TimeProfit"] > curPrice :
                    sell(curCoin, curPrice)
                elif CoinInfo[curCoin]["StopLoss"] > curPrice :
                    sell(curCoin, curPrice)
                elif (CoinInfo[curCoin]["BuyPrice"] > 0) & (CoinInfo[curCoin]["BuyPrice"]*1.12 < curPrice) : 
                    sell(curCoin, curPrice)
            #print(CoinInfo)

        except Exception as e :
            message = str(e) + " is Error Occured"
            Prt_and_Slack(message)

if __name__ == '__main__' :
    run()