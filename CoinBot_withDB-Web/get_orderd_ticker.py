import pyupbit
import pandas as pd
import requests
import time

def get_testcases(order_by = 'acc_trade_price_24h', rank = 0) :

    DF = pd.DataFrame(columns=['ticker','rate'])
    tickers = pyupbit.get_tickers('KRW')
    templist = []

    if order_by == 'acc_trade_price_24h':
        querystring = {"markets":tickers}
        url = "https://api.upbit.com/v1/ticker" #업비트 주소2
        headers = {"Accept": "application/json"}
        response = requests.request("GET", url, headers=headers,params=querystring)
        time.sleep(0.2)

        df = pd.DataFrame(response.json())
        sorteddf = df.sort_values("acc_trade_price_24h",ascending=False).iloc[rank:rank+30]["market"]
        templist = sorteddf.tolist()

    elif order_by == 'signed_change_rate':
        for ticker in tickers :
            try:
                temp = pyupbit.get_ohlcv(ticker = ticker, interval= "day", count= 2).iloc[0]
                temp = pd.DataFrame({'ticker':[ticker], 'rate':[temp['open']/temp['close']]})
                DF = pd.concat([DF,temp])
                print(DF)
            except Exception as e:
                continue
        templist = DF.sort_values('rate', ascending= False).iloc[rank:rank+30]['ticker'].tolist()

    return templist

if __name__ == '__main__':
    print(get_testcases('acc_trade_price_24h'))
    print(get_testcases('signed_change_rate'))