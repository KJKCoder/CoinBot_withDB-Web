from django.urls import path
from . import views

app_name = 'searchData'
urlpatterns = [
    path('', views.index, name = 'index'),
    path('total/', views.total, name = 'total'),
    path('filter/', views.filter, name = 'filter'),
    path('ordered/date', views.ordered_Date, name = 'ordered_Date'),
    path('ordered/ticker', views.ordered_Ticker, name = 'ordered_Ticker'),
]