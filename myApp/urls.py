from django.urls import path
from . import views

urlpatterns =[
    path("", views.home, name="first page"),
    path("get_data/", views.get_data, name="download historical data"),
    path("backtest/", views.backtest, name="backtesting rsi"),
]