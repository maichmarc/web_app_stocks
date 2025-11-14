from django.contrib import admin
from .models import Companies, DailyPrices

admin.site.register(Companies)
admin.site.register(DailyPrices)