import sqlite3
import pandas as pd
import pyupbit
import time
from datetime import datetime, timedelta

start_time = '09:00'
limit_day = datetime(2022, 8, 1, 9, 00, 00, 00)
day_count = 10
tickers = ['KRW-BTC','KRW-ETH']
con = sqlite3.connect("CoinBotWeb/db.sqlite3")
cursor = con.cursor()
con.close()

def Connection_open(DataBase):
    global con, cursor
    con = sqlite3.connect(f"{DataBase}")
    cursor = con.cursor()
    return con

def Connection_close(DataBase):
    global con, cursor
    cursor.close()
    con.close()
    return f'{DataBase} closed'

#이평선 가져오기
def get_MA(to, ticker):
    temp = pyupbit.get_ohlcv(ticker, interval = "day", count = 16, to = to)
    time.sleep(0.1)
    MA = temp['close'].rolling(15).mean().iloc[-1]
    return round(MA, 2)

#오픈 가격 가져오기
def get_open(to, ticker):
    temp = pyupbit.get_ohlcv(ticker, interval = "day", count = 1, to = to)
    time.sleep(0.1)
    open = temp.iloc[0]['close']
    return open

#날짜 데이터 입력 초기 start_day는 Datetime으로 입력
def record_Date_init(strat_day, count):
    Date_Start = [(strat_day + timedelta(i-count)) for i in range(0,count)]
    Date_End = [cur + timedelta(1) for cur in Date_Start]
    raw_data = {'Date_Start':Date_Start, 'Date_End':Date_End}
    DF = pd.DataFrame(raw_data)

    for cur in DF.itertuples():
        sql = "INSERT INTO searchData_날짜(Date_Start, Date_End) VALUES(?,?)"
        cursor.execute(sql, (str(cur[1]), str(cur[2])))
    con.commit()

#btc_eth 데이터 입력 초기
def record_ma_op_init():
    readed_DF = pd.read_sql("SELECT ID, Date_Start FROM searchData_날짜", con, index_col = 'ID')
    for cur in readed_DF.itertuples():
        sql = "INSERT INTO searchData_btc_eth(Ticker, OpenPrice, MA15, 날짜_ID_id) VALUES(?,?,?,?)"
        
        for ticker in tickers:
            cursor.execute(sql, (ticker, get_open(cur[1], ticker), get_MA(cur[1], ticker), cur[0]))
    con.commit()

#Date 데이터 베이스의 마지막 ID 가져오기
def get_DateID_last():
    try :
        id = cursor.execute(f"SELECT ID FROM searchData_날짜 \
                              ORDER BY ID DESC").fetchall()[0][0]
    except Exception as e :
        raise Exception(f"DB get_DateID_last : {str(e)}")
    return id

#날짜 테이블 레코드 추가// date 전달할 때는 date()를 받음
def record_date(date):
    try :
        date_start = datetime.strftime(date, '%Y-%m-%d 09:00:00')
        date_End = datetime.strftime(date + timedelta(days=1), '%Y-%m-%d 09:00:00')
        sql = f"INSERT INTO searchData_날짜 \
                (Date_Start, Date_End) VALUES(?,?)"
        cursor.execute(sql, (str(date_start), str(date_End)))
        con.commit()
    except Exception as e :
        raise Exception(f"DB record_date : {str(e)}")
    return id


#거래 테이블 레코드 추가// 날짜의 ID를 전달
def record_trade(ID, ticker= 'no-ticker', BuyPrice= -1, SoldPrice= -1, BuyTime= 'no-time', SoldTime='no-time', IsDummy= False):
    try :
        sql = f"INSERT INTO searchData_거래 \
            (Ticker, BuyPrice, SoldPrice, BuyTime, SoldTime, IsDummy, 날짜_ID_id) VALUES(?,?,?,?,?,?,?)"
        cursor.execute(sql, (ticker, BuyPrice, SoldPrice, str(BuyTime), str(SoldTime), IsDummy, ID))
        con.commit()
    except sqlite3.Error as e :
        raise Exception(f"DB record_trade : {str(e)}")
    


#btc_eth 테이블 레코드 추가// 날짜의 ID를 전달
def record_btc_eth(ID, ticker = 'KRW-BTC', OpenPrice = -1, MA15 = -1):
    try :
        sql = f"INSERT INTO searchData_btc_eth \
            (Ticker, OpenPrice, MA15, 날짜_ID_id) VALUES(?,?,?,?)"
        cursor.execute(sql, (ticker, OpenPrice, MA15, ID))
        con.commit()
    except Exception as e :
        raise Exception(f"DB record_btc_eth : {str(e)}")

if __name__ == '__main__':
    

    record_date(datetime.now().date())

    Date_ID = get_DateID_last()
    record_btc_eth(Date_ID, 'KRW-BTC', get_open(datetime.now(), 'KRW-BTC'), get_MA(datetime.now(), 'KRW-BTC'))
    record_btc_eth(Date_ID, 'KRW-ETH', get_open(datetime.now(), 'KRW-ETH'), get_MA(datetime.now(), 'KRW-ETH'))

    record_trade(Date_ID, 'KRW-XRP', 500, 550, datetime(2022,8,4,10,5,0), datetime.now(), True)
    record_trade(Date_ID, 'KRW-NEO', 150, 152, datetime(2022,8,4,9,16,0), datetime.now(), True)
    #record_btc_eth(limit_day.date(), 'KRW-ETH', get_open(limit_day,'KRW-ETH'), get_MA(limit_day,'KRW-ETH'))
