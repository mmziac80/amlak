# -*- coding: utf-8 -*-
from django_filters import FilterSet
from django.db import models
from django_filters.widgets import RangeWidget
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

import django_filters
from django.db.models import Q
from .models import  Property,SaleProperty, RentProperty, DailyRentProperty
from .constants import (
    PROPERTY_TYPE_CHOICES,
    DISTRICT_CHOICES,
    DOCUMENT_TYPE_CHOICES,
    DIRECTION_CHOICES,
    PROPERTY_STATUS_CHOICES
)
FILTER_OVERRIDES = {
    models.JSONField: {
        'filter_class': django_filters.CharFilter,
        'extra': lambda f: {
            'lookup_expr': 'icontains',
        },
    }
}

class BasePropertyFilter(django_filters.FilterSet):
    """فیلترهای پایه برای همه انواع املاک"""
    
    # فیلترهای متراژ
    min_area = django_filters.NumberFilter(field_name='area', lookup_expr='gte')
    max_area = django_filters.NumberFilter(field_name='area', lookup_expr='lte')
    
    # فیلترهای تعداد اتاق
    min_rooms = django_filters.NumberFilter(field_name='rooms', lookup_expr='gte')
    max_rooms = django_filters.NumberFilter(field_name='rooms', lookup_expr='lte')
    
    # فیلترهای طبقه
    floor = django_filters.NumberFilter()
    min_floor = django_filters.NumberFilter(field_name='floor', lookup_expr='gte')
    max_floor = django_filters.NumberFilter(field_name='floor', lookup_expr='lte')
    
    # فیلترهای نوع و منطقه
    property_type = django_filters.ChoiceFilter(choices=PROPERTY_TYPE_CHOICES)
    district = django_filters.ChoiceFilter(choices=DISTRICT_CHOICES)
    document_type = django_filters.ChoiceFilter(choices=DOCUMENT_TYPE_CHOICES)
    direction = django_filters.ChoiceFilter(choices=DIRECTION_CHOICES)
    status = django_filters.ChoiceFilter(choices=PROPERTY_STATUS_CHOICES)
    
    # فیلترهای امکانات
    parking = django_filters.BooleanFilter()
    elevator = django_filters.BooleanFilter()
    storage = django_filters.BooleanFilter()
    balcony = django_filters.BooleanFilter()
    package = django_filters.BooleanFilter()
    security = django_filters.BooleanFilter()
    pool = django_filters.BooleanFilter()
    gym = django_filters.BooleanFilter()
    
    # فیلتر جستجوی متنی
    search = django_filters.CharFilter(method='search_filter')
    
    # فیلترهای تاریخ
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    location = django_filters.CharFilter(method='filter_location')


    class Meta:
        model = Property
        fields = '__all__'
        filter_overrides = {
            models.JSONField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                }
            },
            gis_models.PointField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'method': 'filter_location',
                }
            },
        }
    def filter_location(self, queryset, name, value):
        """فیلتر املاک بر اساس موقعیت و شعاع
        فرمت ورودی: 'عرض جغرافیایی,طول جغرافیایی,شعاع به کیلومتر'
        """
        try:
            lat, lng, radius = map(float, value.split(','))
            point = Point(lng, lat, srid=4326)
            return queryset.filter(location__distance_lte=(point, D(km=radius)))
        except (ValueError, TypeError, IndexError):
            return queryset




    def search_filter(self, queryset, name, value):
        """جستجو در عنوان، توضیحات و آدرس"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(address__icontains=value)
        )
    

class SalePropertyFilter(BasePropertyFilter):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = SaleProperty
        exclude = ['location']


class RentPropertyFilter(BasePropertyFilter):
    min_deposit = django_filters.NumberFilter(field_name='deposit', lookup_expr='gte')
    min_rent = django_filters.NumberFilter(field_name='monthly_rent', lookup_expr='gte')
    # فیلترهای مخصوص اجاره

   
    class Meta:
        model = RentProperty
        exclude = ['location']

class DailyRentPropertyFilter(BasePropertyFilter):
    min_price = django_filters.NumberFilter(field_name='daily_price', lookup_expr='gte')
    available_date = django_filters.DateFilter(method='filter_availability')
    # فیلترهای مخصوص اجاره روزانه

    class Meta:
        model = DailyRentProperty
        exclude = ['location']
        
class PropertySearchFilter(django_filters.FilterSet):
    """فیلتر پیشرفته برای جستجوی همه انواع املاک"""
    price_range = django_filters.RangeFilter(field_name='price')
    area_range = django_filters.RangeFilter(field_name='area')
    property_types = django_filters.MultipleChoiceFilter(
        field_name='property_type',
        choices=PROPERTY_TYPE_CHOICES
    )
    districts = django_filters.MultipleChoiceFilter(
        field_name='district',
        choices=DISTRICT_CHOICES
    )
    
    class Meta:
        model = SaleProperty
        fields = [
            'price_range', 'area_range',
            'property_types', 'districts',
            'rooms', 'parking', 'elevator'
        ]

