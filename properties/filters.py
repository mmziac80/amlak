import django_filters
from django.db.models import Q
from .models import SaleProperty, RentProperty, DailyRentProperty
from .constants import (
    PROPERTY_TYPE_CHOICES,
    DISTRICT_CHOICES,
    DOCUMENT_TYPE_CHOICES,
    DIRECTION_CHOICES,
    PROPERTY_STATUS_CHOICES
)

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

    def search_filter(self, queryset, name, value):
        """جستجو در عنوان، توضیحات و آدرس"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(address__icontains=value)
        )

class SalePropertyFilter(BasePropertyFilter):
    """فیلترهای مخصوص املاک فروشی"""
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    is_exchangeable = django_filters.BooleanFilter()
    is_negotiable = django_filters.BooleanFilter()

    class Meta:
        model = SaleProperty
        fields = '__all__'

class RentPropertyFilter(BasePropertyFilter):
    """فیلترهای مخصوص املاک اجاره‌ای"""
    min_deposit = django_filters.NumberFilter(field_name='deposit', lookup_expr='gte')
    max_deposit = django_filters.NumberFilter(field_name='deposit', lookup_expr='lte')
    min_rent = django_filters.NumberFilter(field_name='monthly_rent', lookup_expr='gte')
    max_rent = django_filters.NumberFilter(field_name='monthly_rent', lookup_expr='lte')
    is_convertible = django_filters.BooleanFilter()
    has_transfer_fee = django_filters.BooleanFilter()

    class Meta:
        model = RentProperty
        fields = '__all__'

class DailyRentPropertyFilter(BasePropertyFilter):
    """فیلترهای مخصوص املاک اجاره روزانه"""
    min_price = django_filters.NumberFilter(field_name='daily_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='daily_price', lookup_expr='lte')
    min_days = django_filters.NumberFilter(field_name='minimum_days', lookup_expr='gte')
    max_days = django_filters.NumberFilter(field_name='maximum_days', lookup_expr='lte')
    min_capacity = django_filters.NumberFilter(field_name='capacity', lookup_expr='gte')
    max_capacity = django_filters.NumberFilter(field_name='capacity', lookup_expr='lte')

    class Meta:
        model = DailyRentProperty
        fields = '__all__'

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
