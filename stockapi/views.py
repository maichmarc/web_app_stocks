from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Companies, DailyPrices, DisplayData
from . serializers import CompanySerializer, DailypriceSerializer, DateRangeSerializer, PriceBetweenDateSerializer
from django.shortcuts import render, redirect
from django.db import connection
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from . import views
from datetime import datetime, date
import pandas_ta as ta
from sqlalchemy import create_engine
from django.conf import settings
import os


# import re

db_settings = settings.DATABASES['default']
dialect = "postgresql+psycopg2"


DATABASE_URL = (
        f"{dialect}://{os.environ.get['PGUSER']}:{os.environ.get['PGPASSWORD']}"
        f"@{os.environ.get['PGHOST']}:{os.environ.get['PGPORT']}/{os.environ.get['PGDATABASE']}"
    )

DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)

query = """SELECT c.name, c.code, d.date, d.day_low, d.day_high, d.day_price, d.volume  
            FROM daily_prices as d
            JOIN
            companies as c
            ON c.id = d.company_id"""

# df = pd.read_sql(query, connection)
df = pd.read_sql(query, engine)
codes = df['code'].unique()
names = df['name'].unique()

@api_view(['GET'])
def stock_list(request):
    if request.method == 'GET':
        stock_names = Companies.objects.all()
        serializer = CompanySerializer(stock_names, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def daily_price_list(request):
    if request.method == 'GET':
        price_list = DailyPrices.objects.all()
        serializer = DailypriceSerializer(price_list, many=True)
        return JsonResponse(serializer.data, safe=False)
    
class StockPriceByCodeDate(APIView):
    def get(self, request):
        code = request.GET.get('code')
        date = request.GET.get('date')

        if not code or not date:
            return Response({'error': 'Both "code" and "date" are required.'}, status=400)

        # try:
        stock = DailyPrices.objects.select_related('company').get(company__code=code.upper(), date=date)
        serializer = DailypriceSerializer(stock)
        return Response(serializer.data)

"""
UNUSED
def ensure_date(value):
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    raise TypeError(f"Unsupported type: {type(value)}")
"""

"""
WRONG
class StockPriceBetweenDates(APIView):
        def get(self, request):
            # code = request.query_params.get('code')
            # start_date = request.query_params.get('start_date')
            # end_date = request.query_params.get('end_date')

            code = request.GET.get('code')
            start_date = datetime.fromisoformat(request.GET.get('start_date')).date()
            # print(start_date_str, type(start_date_str))
            # start_date = ensure_date(start_date_str) 
            # if start_date:
            # start_date = datetime.fromisoformat(start_date)
            print(start_date, type(start_date))
            end_date = datetime.fromisoformat(request.GET.get('end_date')).date()
            # end_date = ensure_date(end_date_str)
            # if end_date:
            # end_date = datetime.fromisoformat(end_date)

            if not code or not start_date or not end_date:
                return Response({'error': ' "code", "start_date" and "end_date" are required.'}, status=400)
            


            # try:
            stock = DailyPrices.objects.select_related('company').filter(company__code=code.upper(), date__range = [start_date, end_date])
            serializer = PriceBetweenDateSerializer(stock)
            return Response(serializer.data)
            """

class StockPriceBetweenTwoDates(APIView):
        #This is correct
        def get(self, request):
            serializer = DateRangeSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            code = serializer.validated_data.get('code')
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
         

            # if not code or not start_date or not end_date:
            #     return Response({'error': ' "code", "start_date" and "end_date" are required.'}, status=400)
            
            stock = DailyPrices.objects.filter(company__code=code.upper(), date__range = [start_date, end_date])
            serializer_out = PriceBetweenDateSerializer(stock, many=True)
            return Response(serializer_out.data)

# def date_prices(request):
#     if request.method == 'GET':
#         return render(request, 'home.html')
#     else:
#         date = request.POST['date']
#         cursor = connection.cursor()
#         cursor.execute("""SELECT c.name, c.code, d.date, d.day_low, d.day_high, d.day_price, d.volume  FROM daily_prices as d
#                             JOIN
#                             companies as c
#                             ON c.id = d.company_id
#                             WHERE d.date = %s
                            
#                     """, [date])
#         result = cursor.fetchall()
#         return render(request, 'index.html', {'DisplayData':result})
    
def date_prices_w_o_date(request):
    if request.method == 'GET':
        cursor = connection.cursor()
        cursor.execute(""" SELECT date FROM daily_prices
                                    ORDER BY date DESC
                                    LIMIT 1;
                            """)
        row = cursor.fetchone()         # fetch one row from the result
        date = row[0]
        
        cursor.execute("""SELECT c.name, c.code, d.date, d.day_low, d.day_high, d.day_price, d.volume  FROM daily_prices as d
                        JOIN
                        companies as c
                        ON c.id = d.company_id
                        WHERE d.date = %s
                        
                """, [date])
        result = cursor.fetchall()
        # print(date)
        return render(request, 'index.html', {'DisplayData':result})
    else:    
        dates = request.POST('date_of_stock')
    #     cursor = connection.cursor()
    #     cursor.execute("""SELECT c.name, c.code, d.date, d.day_low, d.day_high, d.day_price, d.volume  FROM daily_prices as d
    #                         JOIN
    #                         companies as c
    #                         ON c.id = d.company_id
    #                         WHERE d.date = %s
                            
    #                 """, [date])
    #     result = cursor.fetchall()
        return redirect('stockprices_date', dates)#, date)#{'DisplayData':result})
    
def date_prices(request, date):
    # if request.method == 'GET':
    #     cursor = connection.cursor()
    #     cursor.execute(""" SELECT date FROM daily_prices
    #                                 ORDER BY date DESC
    #                                 LIMIT 1;
    #                         """)
    #     row = cursor.fetchone()         # fetch one row from the result
    #     date = row[0]
        
    #     cursor.execute("""SELECT c.name, c.code, d.date, d.day_low, d.day_high, d.day_price, d.volume  FROM daily_prices as d
    #                     JOIN
    #                     companies as c
    #                     ON c.id = d.company_id
    #                     WHERE d.date = %s
                        
    #             """, [date])
    #     result = cursor.fetchall()
    #     print(date)
    #     return render(request, 'index.html', {'DisplayData':result})
    # else:    
        date = request.POST.get('date_of_stock')
        cursor = connection.cursor()
        cursor.execute("""SELECT c.name, c.code, d.date, d.day_low, d.day_high, d.day_price, d.volume  FROM daily_prices as d
                            JOIN
                            companies as c
                            ON c.id = d.company_id
                            WHERE d.date = %s
                            
                    """, [date])
        result = cursor.fetchall()
        # print(dates)
        return render(request, 'index.html', {'DisplayData':result})

    
def retrive_stock_info(stock_code):
    # if request.method == 'GET':
        # cursor = connection.cursor()
    

    query = """SELECT c.name, c.code, c.sector, c.brief, d.date, d.day_low, d.day_high, 
            d.day_price, d.volume  
            FROM daily_prices as d
            JOIN
            companies as c
            ON c.id = d.company_id
            WHERE d.date > '2011-12-31'"""

    # df = pd.read_sql(query, connection)
    df = pd.read_sql(query, engine)
    codes = df['code'].unique()
    names = df['name'].unique()
    stock_df = df[df['code'] == stock_code]
    stock_df['previous'] = stock_df['day_price'].shift(1)
    stock_df['50MA'] = stock_df['day_price'].rolling(window = 50).mean()
    stock_df['RSI'] = ta.rsi(close=stock_df['day_price'], length=14)
    stock_df['EMA12'] = stock_df['day_price'].ewm(span=12).mean()
    stock_df['EMA26'] = stock_df['day_price'].ewm(span=26).mean()
    stock_df['MACD'] = stock_df['EMA12'] - stock_df['EMA26']
    stock_df['signal'] = stock_df['MACD'].ewm(span=9).mean()
    
    # stock_df.to_csv(f'{stock_code}_df.csv')
    return stock_df#, codes, names

# class createGraphObjects()

def add_200MA(fig,df):
    
    fig.add_trace(go.Scatter(
                  x=df['date'],
                  y=df['200MA'],
                  line = dict(color='#e0e0e0'),
                  name = '200 day MA'
                  )
    )
    return fig

def create_candle_sticks(df):
        fig = go.Figure(data=[
                            go.Candlestick(
                                x= df['date'],
                                open= df['previous'],
                                low= df['day_low'],
                                high= df['day_high'],
                                close= df['day_price']),

                            go.Scatter(x=df['date'], y=df['RSI'], 
                                      line=dict(color='#e0e0e0'), 
                                      name='RSI', yaxis="y2"),

                            go.Scatter(x=df['date'],
                                        y=df['50MA'],
                                        line=dict(color='#6c22d3'), 
                                        name= '50 day MA')
    ])
        # fig.add_trace(
        # go.Scatter(
        #     x=df['date'],
        #     y=df['50MA'],
        #     line=dict(color='#e0e0e0'), 
        #     name= '50 day MA'
        # ))
        fig.update_layout(autosize=True,
                            yaxis_domain=[0.3, 1],
                            yaxis2={"domain": [0, 0.20], "title": "RSI"},)
        fig.update_layout(margin={'t':0, 'l':0, 'r':0, 'b':0})
        fig.update_layout(xaxis_rangeslider_visible=False, template='plotly_dark', xaxis_title='Date',
                        yaxis_title='Price (Kshs.)' )
        
        fig.add_hline(
            y=70, 
            line_dash="dash", 
            line_color="red", 
            opacity=0.8, 
            line_width=1.5,
            yref="y2"
            )
        
        fig.add_hline(
            y=30, 
            line_dash="dash", 
            line_color="green", 
            opacity=0.8, 
            line_width=1.5,
            yref="y2"
            )
        
        fig.add_hline(
            y=50, 
            line_dash="dash", 
            line_color="blue", 
            opacity=0.8, 
            line_width=1.5,
            yref="y2"
            )

        return fig


    
def add_MA_on_candlestick(fig, df):
   
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['50MA'],
            line=dict(color='#e0e0e0')
        )
    )
    return fig

def create_price_MACD(df):
    fig = go.Figure(data=[
                            go.Scatter(
                                x= df['date'],
                                y=df['day_price'], 
                                line=dict(color="#e0eef0"), 
                                name='prices'),# yaxis="y2"),

                            go.Scatter(x=df['date'], y=df['signal'], 
                                      line=dict(color="#f80505"), 
                                      name='signal', yaxis="y2"),

                            go.Scatter(x=df['date'],
                                        y=df['MACD'],
                                        line=dict(color="#09f50d"), 
                                        name= 'MACD', yaxis="y2")
    ])
      
    fig.update_layout(autosize=True,
                        yaxis_domain=[0.4, 1],
                        yaxis2={"domain": [0, 0.4], "title": "MACD"},)
    fig.update_layout(margin={'t':0, 'l':0, 'r':0, 'b':0})
    fig.update_layout(xaxis_rangeslider_visible=False, template='plotly_dark', xaxis_title='Date',
                    yaxis_title='Price (Kshs.)' )

    return fig

def create_MACD(df):
    fig = go.Figure(data=[
                            go.Scatter(x=df['date'], y=df['signal'], 
                                      line=dict(color="#f80505"), 
                                      name='signal'),#, yaxis="y2"),

                            go.Scatter(x=df['date'],
                                        y=df['MACD'],
                                        line=dict(color="#09f50d"), 
                                        name= 'MACD')#, yaxis="y2")
    ])
      
    # fig.update_layout(autosize=True,
    #                     yaxis_domain=[0.3, 1],
    #                     yaxis2={"domain": [0, 0.20], "title": "MACD"},)
    fig.update_layout(margin={'t':0, 'l':0, 'r':0, 'b':0})
    fig.update_layout(template='plotly_dark', xaxis_title='Date', yaxis_title='MACD' )

    return fig


        
     



def display_graph(request, stock_code):
    stock_df = retrive_stock_info(stock_code)
    stock_name = stock_df['name'].values[0]
    stock_sector = stock_df['sector'].values[0]
    stock_brief = stock_df['brief'].values[0]
    latest_change = stock_df['day_price'].values[-1] - stock_df['day_price'].values[-2]
    change_pcnt = latest_change / stock_df['day_price'].values[-1] * 100
    candle_stick = create_candle_sticks(stock_df)
    MACD_chart = create_price_MACD(stock_df)
    # MA_line = add_MA_on_candlestick(candle_stick, stock_df)
    chart_div = pio.to_html(candle_stick, full_html=False, include_plotlyjs='cdn', div_id='ohlc')
    # chart_div_MA = pio.to_html(MA_line, full_html=False, include_plotlyjs='cdn', div_id='ohlc')
    MACD_div = pio.to_html(MACD_chart, full_html=False, include_plotlyjs=False, div_id='macd')
    # print(f'HERE is RSI DIV{RSI_div[:500]}')
    latest_price = stock_df['day_price'].values[-1]
    previous_price = stock_df['day_price'].values[-2]
    volume = stock_df['volume'].values[-1]
    date = stock_df['date'].values[-1]

    context = {
        'code_names':zip(codes, names),
        'chart_div': chart_div,
        'MACD_div' : MACD_div,
        'stock_name': stock_name,
        'stock_code': stock_code,
        'change': latest_change,
        'change_percent': change_pcnt,
        'latest_price':latest_price,
        'previous_price':previous_price,
        'volume':volume,
        'stock_brief':stock_brief,
        'stock_sector':stock_sector,
        'date':date

    }

    return render(request, 'stock_ticker.html', context=context)

def retrive_combined_stock_df():
    # if request.method == 'GET':
        # cursor = connection.cursor()
    query = """SELECT c.name, c.code, d.date, d.day_low, d.day_high, d.day_price, d.change, d.volume  
            FROM daily_prices as d
            JOIN
            companies as c
            ON c.id = d.company_id"""

    # comb_df = pd.read_sql(query, connection)    
    comb_df = pd.read_sql(query, engine)   
    comb_df['pct_change'] = (comb_df['change'] / comb_df['day_price'])*100
    # print(comb_df.head())
    # comb_df.to_csv('asdfa.csv')
    return comb_df

def display_homepage(request):
    comb_df = retrive_combined_stock_df()
    latest_date = comb_df['date'].values[-1]
    latest_df = comb_df[comb_df['date']==latest_date]
    top_10_gainers = latest_df.sort_values(by='pct_change', ascending=False).head(10)
    top_10_losers = latest_df.sort_values(by='pct_change', ascending=True).head(10)
    top_10_movers = latest_df.sort_values(by='volume', ascending=False).head(10)
    
    top_5_gainers = latest_df.sort_values(by='pct_change', ascending=False).head()
    top_5_losers = latest_df.sort_values(by='pct_change', ascending=True).head()
    top_5_movers = latest_df.sort_values(by='volume', ascending=False).head()

    gainers = top_5_gainers.to_dict(orient='records')
    losers = top_5_losers.to_dict(orient='records')
    movers = top_5_movers.to_dict(orient='records')

  
    # context = {
    #     # 'gainers':top_10_gainers.to_html(index=False),
    #     # 'losers': top_10_losers,
    #     # 'movers': top_10_movers,
    #     'date': latest_date

    # }
    print(latest_date)
    return render(request, 
                  'home.html', 
                  {
            'gainer_rows': gainers,
            'loser_rows': losers,
            'movers_rows': movers,
            'date': latest_date
        }
             )



def stock_index(request):
    return redirect('stockticker', 'EGAD')

def boots(request):
    return render(request, 'a_html.html')

def stock_price_api(request):
    return render(request, 'stock_api.html')