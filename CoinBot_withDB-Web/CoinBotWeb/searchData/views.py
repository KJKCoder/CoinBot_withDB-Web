from turtle import left
from django.shortcuts import render
from .models import *
from django.db import connection
import pandas as pd
# Create your views here.

def my_custom_sql(date_id = None, ticker = None):

    if date_id == None and ticker == None:
        where_sql = "WHERE 1"
    elif date_id != None and ticker == None:
        where_sql = f"WHERE 날짜_ID_id = {date_id}"
    elif date_id == None and ticker != None:
        where_sql = f"WHERE Ticker = '{ticker}'"
    else:
        where_sql = f"WHERE (날짜_ID_id = {date_id}) and (Ticker = '{ticker}')"

    sql = f'SELECT 날짜_ID_id, Ticker, round(SoldPrice/BuyPrice,4) as Prf, round((10 * (SoldPrice/BuyPrice) + 90) / (100),4) as r_Prf FROM searchData_거래\
            {where_sql}'

    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = dictfetchall(cursor)
    return result

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def total_out(date_ID = None, ticker= None):
    result = {}
    try:
        DF = pd.DataFrame(my_custom_sql(date_ID, ticker))['r_Prf']

        result['Profit'] = round(DF.cumprod().iloc[-1],4)
        result['Trade'] = DF.count()
    except:
        return None
    return result
    
def find_date_ID(date):
    if(date==None): return None
    try:
        with connection.cursor() as cursor:
            id = cursor.execute(f"SELECT ID FROM searchData_날짜 \
                                WHERE substr(Date_Start,1,10) = '{date}'").fetchall()[0][0]
    except :
        return -1
    return id

def find_Date_Start(date_ID):
    if(date_ID==None): return None
    try:
        with connection.cursor() as cursor:
            Date_Start = cursor.execute(f"SELECT Date_Start FROM searchData_날짜 \
                                WHERE ID = {date_ID}").fetchall()[0][0]
    except :
        return -1
    return Date_Start

def my_ordered_sql(group_by = '날짜_ID_id' , count = 30):

    if group_by == '날짜_ID_id': 
        sql = f'SELECT 날짜_ID_id, Ticker, round(SoldPrice/BuyPrice,4) as Prf, round((10 * (SoldPrice/BuyPrice) + 90) / (100),4) as r_Prf FROM searchData_거래\
                ORDER BY 날짜_ID_id DESC\
                LIMIT 300'
    else:
        sql = f'SELECT 날짜_ID_id, Ticker, round(SoldPrice/BuyPrice,4) as Prf, round((10 * (SoldPrice/BuyPrice) + 90) / (100),4) as r_Prf FROM searchData_거래\
                ORDER BY 날짜_ID_id DESC'

    with connection.cursor() as cursor:
        cursor.execute(sql)
        DF = pd.DataFrame(dictfetchall(cursor))
    
    DF['trade'] = 1
    DF['Prf'] = DF.groupby(group_by)['Prf'].cumprod()
    DF['r_Prf'] = DF.groupby(group_by)['r_Prf'].cumprod()
    DF['trade'] = DF.groupby(group_by)['trade'].cumsum()

    DF = DF.groupby(group_by,as_index=False, sort= False).max().head(count)
 
    if group_by == '날짜_ID_id':
        DF['날짜'] = DF.apply(lambda x: find_Date_Start(x['날짜_ID_id']), axis=1)
        DF = DF.drop(columns=['날짜_ID_id','Ticker']).set_index('날짜')
    else : 
        DF = DF.sort_values('trade', ascending= False).set_index('Ticker').drop(columns=['날짜_ID_id'])

    return DF


# 웹 페이지 뷰

def index(request):
    return render(request, 'searchData/index.html')

def total(request):
    total_Data = total_out()
    context = {'total_Data': total_Data}
    return render(request, 'searchData/total.html', context)

def filter(request):
    date = request.POST['date'] ; ticker = request.POST['ticker']
    if (date == ''): date= None
    if (ticker == ''): ticker= None
    filter_Data = total_out(find_date_ID(date), ticker)
    context = {'filter_Data': filter_Data,
                'date' : date,
                'ticker' : ticker}
    return render(request, 'searchData/filter.html', context)

def ordered_Date(request):
    DF = my_ordered_sql('날짜_ID_id', 30)
    ordered_Data = DF.to_html()

    context = {'ordered_Data': ordered_Data,}
    return render(request, 'searchData/ordered/date.html', context)

def ordered_Ticker(request):
    DF = my_ordered_sql('Ticker', 30)
    ordered_Ticker = DF.to_html()

    context = {'ordered_Ticker': ordered_Ticker,}
    return render(request, 'searchData/ordered/ticker.html', context)