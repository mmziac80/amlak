from rest_framework import serializers
from django.utils import timezone

from .models import (
    SaleProperty, 
    RentProperty, 
    DailyRentProperty,
    PropertyImage,
    PropertyFeature,
    Visit,
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
            'is_available', 'created_at', 'updated_at'
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
            'id', 'property', 'property_title', 'name',
            'phone', 'visit_time', 'status', 'created_at'
        ]
        read_only_fields = ['status']

    def validate_visit_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "تاریخ بازدید نمی‌تواند در گذشته باشد"
            )
        return value

from rest_framework import serializers
from .models import SaleProperty, RentProperty, DailyRentProperty

class PropertySerializer(serializers.ModelSerializer):
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    district_display = serializers.CharField(source='get_district_display', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        fields = [
            'id', 'title', 'description', 'property_type', 'property_type_display',
            'district', 'district_display', 'address', 'area', 'rooms',
            'floor', 'total_floors', 'parking', 'elevator', 'storage',
            'balcony', 'created_at', 'owner', 'owner_name'
        ]
        
    def get_serializer_class(self):
        if isinstance(self.instance, SaleProperty):
            return SalePropertySerializer
        elif isinstance(self.instance, RentProperty):
            return RentPropertySerializer
        return DailyRentPropertySerializer
