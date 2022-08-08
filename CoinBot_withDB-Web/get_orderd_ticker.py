from http.client import FORBIDDEN
from time import strftime
from urllib import response
import requests
import pyupbit
import pandas as pd
import datetime
import threading

DF = pd.DataFrame()
responses = []
tickers = pyupbit.get_tickers("KRW")

def get_Data(ticker):
    global DF, responses

    url = f'https://crix-api-endpoint.upbit.com/v1/crix/candles/days/?code=CRIX.UPBIT.{ticker}&count=1&to={date}'
    response = requests.request("GET",url)
    responses.append(response.json())


def get_testcases(target_date, order_by, rank_start = 0):
    global date, DF, responses
    date = target_date.strftime('%Y-%m-%d%%20%H:%M:%S')
    
    threads = []
    responses = []
    DF = pd.DataFrame()

    for ticker in tickers:
        t = threading.Thread(target=get_Data, args=(ticker,), daemon=True)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()     

    for r in responses:
        DF = DF.append(r, ignore_index= True)
    DF = DF.set_index('code').loc[:,[order_by]]
    
    sorteddf = DF.sort_values(by=[order_by],ascending=False).reset_index(drop=False).loc[rank_start:rank_start+30]
    result = [str(i)[11:] for i in sorteddf['code'].tolist()]
    
    return result


if __name__ == '__main__':
    date=datetime.datetime(2022,8,7,9,0,0)
    target_date = date - datetime.timedelta(1)
    print(target_date)
    print(get_testcases(target_date, "signedChangeRate", 0))