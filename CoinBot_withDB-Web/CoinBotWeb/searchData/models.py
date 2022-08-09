from asyncio import constants
from operator import index
from django.db import models

# Create your models here.

class 날짜(models.Model):
    ID = models.IntegerField(primary_key=True, unique=True, db_index= True, null= False, auto_created= True)
    Date_Start = models.DateTimeField(unique= True, auto_now_add= True, null= False)
    Date_End = models.DateTimeField(unique= True, auto_now_add= True, null= False)
    class Meta:
       indexes = [
            models.Index(fields=['ID',], name= '날짜_Index'),
        ]

class 거래(models.Model):
    날짜_ID = models.ForeignKey('날짜', on_delete= models.CASCADE)
    Ticker = models.CharField(null= False, max_length= 10, default= 'no-ticker')
    BuyPrice = models.FloatField(null= True, default= -1)
    SoldPrice = models.FloatField(null= True, default= -1)
    BuyTime = models.TimeField(null= True, auto_now_add= True)
    SoldTime = models.TimeField(null= True, auto_now_add= True)
    IsDummy = models.BooleanField(null= False, default= True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['날짜_ID','Ticker'], name= '거래_PK' )]
        indexes = [models.Index(fields=['날짜_ID','Ticker'], name= '거래_Index'),]

class BTC_ETH(models.Model):
    날짜_ID = models.ForeignKey('날짜', on_delete= models.CASCADE)
    Ticker = models.CharField(null= False, max_length= 10, default= 'KRW-BTC', choices=[('BTC','KRW-BTC'),('ETH','KRW-ETH')])
    OpenPrice = models.FloatField(null= True, default= -1)
    MA15 = models.FloatField(null= True, default= -1)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['날짜_ID','Ticker'], name= 'BTC_ETH_PK' )]
        indexes = [models.Index(fields=['날짜_ID','Ticker'], name= 'BTC_ETH_Index'),]
