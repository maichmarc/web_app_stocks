from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
# from . models import Companies, DailyPrices, DisplayData
# from . serializers import CompanySerializer, DailypriceSerializer
from django.shortcuts import render, redirect
from django.db import connection
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from . import views
import pandas_ta as ta

# def dta(request):
#     if request.method=='POST':
#         date =  request.POST.get('date_of_stock')
#     return date

# date = dta()
# print(date)

pio.renderers.default = 'browser'

def retrive_stock_info(stock_code):
    # if request.method == 'GET':
        # cursor = connection.cursor()
    query = """SELECT c.name, c.code, d.date, d.day_low, d.day_high, d.day_price, d.volume  
            FROM daily_prices as d
            JOIN
            companies as c
            ON c.id = d.company_id"""

    df = pd.read_sql(query, connection)
    codes = df['code'].unique()
    names = df['name'].unique()
    stock_df = df[df['code'] == stock_code]
    stock_df['previous'] = stock_df['day_price'].shift(1)
    stock_df['50MA'] = stock_df['day_price'].rolling(window = 50).mean()
    stock_df['RSI'] = ta.rsi(close=stock_df['day_price'], length=14)
    # print(stock_df['200MA'])
    return stock_df#, codes, names

def create_RSI(df):
    fig = go.Figure(data=[go.Scatter(x=df['date'], y=df['RSI'], 
                                      line=dict(color='#e0e0e0'), 
                                      name='RSI')])

    fig.update_layout(title= "Close Price and RSI")

    return fig

stock_df = retrive_stock_info('SCOM')

fig = create_RSI(stock_df)

fig.show()

