from rest_framework import serializers
from .models import Companies, DailyPrices, DisplayData

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Companies
        fields = ['code', 'name']

class DailypriceSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    class Meta:
        model = DailyPrices
        fields = ['company', 'date', 'day_low', 'day_high', 'day_price', 'volume']

    
class DateRangeSerializer(serializers.Serializer):
    code = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()

    def validate(self, data):
        # Optional: Add validation to ensure end_date is after start_date
        if data['start_date'] and data['end_date'] and data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data
  

class PriceBetweenDateSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    class Meta:
        model = DisplayData
        fields = ['company', 'date', 'day_low', 'day_high', 'day_price', 'volume']    


    

