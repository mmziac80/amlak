# -*- coding: utf-8 -*-

from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal

from .models import (
    SaleProperty, 
    RentProperty, 
    DailyRentProperty,
    PropertyImage,
    PropertyFeature,
    Visit,
    Booking,
    Property,
    Booking
)

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_main', 'property']

class PropertyFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyFeature
        fields = ['id', 'name', 'icon']

class SalePropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    features = PropertyFeatureSerializer(many=True, read_only=True)
    district_display = serializers.CharField(source='get_district_display')
    property_type_display = serializers.CharField(source='get_property_type_display')
    price_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = SaleProperty
        fields = [
            'id', 'title', 'description', 'property_type',
            'property_type_display', 'district', 'district_display',
            'price', 'price_formatted', 'price_per_meter',
            'area', 'rooms', 'floor', 'total_floors',
            'parking', 'elevator', 'storage', 'balcony',
            'building_age', 'images', 'features',
            'created_at', 'updated_at', 'is_active'
        ]

    def get_price_formatted(self, obj):
        return f"{obj.price:,} تومان"

class RentPropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    features = PropertyFeatureSerializer(many=True, read_only=True)
    district_display = serializers.CharField(source='get_district_display')
    property_type_display = serializers.CharField(source='get_property_type_display')
    
    class Meta:
        model = RentProperty
        fields = [
            'id', 'title', 'description', 'property_type',
            'property_type_display', 'district', 'district_display',
            'deposit', 'rent', 'area', 'rooms',
            'floor', 'total_floors', 'parking', 'elevator',
            'storage', 'balcony', 'building_age',
            'images', 'features', 'created_at', 'updated_at',
            'is_active'
        ]

class DailyRentPropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    features = PropertyFeatureSerializer(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyRentProperty
        fields = [
            'id', 'title', 'description', 'area', 'rooms',
            'daily_price', 'max_guests', 'property_type',
            'address', 'images', 'features', 'wifi',
            'parking', 'kitchen', 'tv', 'washing_machine',
            'is_available', 'min_stay','created_at', 'updated_at'
        ]

    def get_is_available(self, obj):
        check_in = self.context.get('check_in')
        check_out = self.context.get('check_out')
        if not (check_in and check_out):
            return True
        
        return obj.is_available_for_dates(check_in, check_out)

class BookingSerializer(serializers.ModelSerializer):
    total_nights = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    property_details = DailyRentPropertySerializer(source='property', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'property', 'property_details', 'user',
            'check_in', 'check_out', 'guests_count',
            'total_nights', 'total_price', 'status',
            'created_at', 'payment_id', 'payment_date'
        ]
        read_only_fields = ['status', 'payment_id', 'payment_date']

    def get_total_nights(self, obj):
        return (obj.check_out - obj.check_in).days

    def get_total_price(self, obj):
        nights = self.get_total_nights(obj)
        return obj.property.daily_price * nights

    def validate(self, data):
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError(
                "تاریخ ورود باید قبل از تاریخ خروج باشد"
            )
        
        if data['guests_count'] > data['property'].max_guests:
            raise serializers.ValidationError(
                "تعداد مهمان‌ها بیشتر از ظرفیت اقامتگاه است"
            )
        
        if not data['property'].is_available_for_dates(
            data['check_in'], data['check_out']
        ):
            raise serializers.ValidationError(
                "این تاریخ قبلاً رزرو شده است"
            )
        
        return data

class VisitSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    
    class Meta:
        model = Visit
        fields = [
            'id', 'property', 'visitor', 
            'visit_date', 'visit_time', 'notes',
            'status', 'created_at'
        ]
        read_only_fields = ['status', 'visitor']

    def validate_visit_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "تاریخ بازدید نمی‌تواند در گذشته باشد"
            )
        return value

from decimal import Decimal

class PropertySerializer(serializers.ModelSerializer):
    latitude = serializers.DecimalField(
        max_digits=10, 
        decimal_places=7,
        min_value=Decimal('-90'),
        max_value=Decimal('90')
    )
    longitude = serializers.DecimalField(
        max_digits=10, 
        decimal_places=7,
        min_value=Decimal('-180'),
        max_value=Decimal('180')
    )
class PropertyLocationSerializer(serializers.ModelSerializer):
    price_display = serializers.SerializerMethodField()
    property_type = serializers.CharField(source='get_property_type_display', read_only=True)
    distance = serializers.FloatField(read_only=True, required=False)

    def get_price_display(self, obj):
        if hasattr(obj, 'saleproperty'):
            return f"قیمت: {obj.saleproperty.total_price:,} تومان"
        elif hasattr(obj, 'rentproperty'):
            return f"ودیعه: {obj.rentproperty.deposit:,} - اجاره: {obj.rentproperty.monthly_rent:,} تومان"
        elif hasattr(obj, 'dailyrentproperty'):
            return f"شبی {obj.dailyrentproperty.daily_price:,} تومان"
        return "قیمت تعیین نشده"



    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance, 'distance'):
            data['distance'] = round(float(instance.distance), 2)
        return data

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'latitude', 'longitude',
            'address', 'deal_type', 'price_display',
            'property_type', 'status', 'distance'
        ]
