from django.contrib import admin
from .models import 날짜, 거래, BTC_ETH

# Register your models here.

admin.site.register(날짜)
admin.site.register(BTC_ETH)
admin.site.register(거래)
