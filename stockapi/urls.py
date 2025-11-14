"""
URL configuration for stockapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('stocks/', views.stock_list),
    path('daily_prices/', views.daily_price_list),
    path('stock_price_details/', views.StockPriceByCodeDate.as_view()),
    path('stock_prices/', views.date_prices_w_o_date, name='stockprices'),
    path('stock_price/<date>', views.date_prices, name='stockprices_date'),
    path('<stock_code>', views.display_graph, name='stockticker'),
    path('boots/', views.boots),
    path('stock_index/', views.stock_index, name='stockindex'),
    path('home/', views.display_homepage, name='home'),
    path('', views.display_homepage, name='home'),
    # path('get_stock_info/', views.StockPriceBetweenDates.as_view(), name='price_between_dates'),
    path('get_stock_information/', views.StockPriceBetweenTwoDates.as_view(), name='price_bet_dates'),
    path('stock_api_info/', views.stock_price_api, name='stock_api'),
    # path('', views.stock_price_api, name='stock_api'),


]
