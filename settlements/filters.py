from django_filters import rest_framework as filters
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Settlement

class SettlementFilter(filters.FilterSet):
    date_from = filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='از تاریخ'
    )
    date_to = filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='تا تاریخ'
    )
    min_amount = filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte',
        label='حداقل مبلغ'
    )
    max_amount = filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte',
        label='حداکثر مبلغ'
    )
    search = filters.CharFilter(
        method='search_filter',
        label='جستجو'
    )
    status = filters.ChoiceFilter(
        choices=Settlement.STATUS_CHOICES,
        label='وضعیت'
    )
    owner = filters.NumberFilter(
        field_name='owner_id',
        label='مالک'
    )
    bank_account = filters.CharFilter(
        lookup_expr='icontains',
        label='شماره حساب'
    )
    processed_by = filters.NumberFilter(
        field_name='processed_by_id',
        label='بررسی شده توسط'
    )
    is_delayed = filters.BooleanFilter(
        method='delayed_filter',
        label='تسویه‌های معوق'
    )
    
    class Meta:
        model = Settlement
        fields = [
            'date_from', 'date_to', 
            'min_amount', 'max_amount',
            'status', 'owner', 
            'bank_account', 'search',
            'processed_by', 'is_delayed'
        ]

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(tracking_code__icontains=value) |
            Q(bank_reference_id__icontains=value) |
            Q(owner__first_name__icontains=value) |
            Q(owner__last_name__icontains=value) |
            Q(owner__phone__icontains=value) |
            Q(owner__email__icontains=value) |
            Q(rejection_reason__icontains=value)
        )

    def delayed_filter(self, queryset, name, value):
        if value:
            delay_threshold = timezone.now() - timedelta(days=7)
            return queryset.filter(
                status='pending',
                created_at__lt=delay_threshold
            )
        return queryset

class SettlementReportFilter(filters.FilterSet):
    year = filters.NumberFilter(
        field_name='created_at__year',
        label='سال'
    )
    month = filters.NumberFilter(
        field_name='created_at__month',
        label='ماه'
    )
    status = filters.ChoiceFilter(
        choices=Settlement.STATUS_CHOICES,
        label='وضعیت'
    )
    owner_type = filters.ChoiceFilter(
        choices=[
            ('individual', 'شخصی'),
            ('business', 'کسب و کار')
        ],
        method='filter_owner_type',
        label='نوع مالک'
    )

    class Meta:
        model = Settlement
        fields = ['year', 'month', 'status', 'owner_type']

    def filter_owner_type(self, queryset, name, value):
        if value == 'business':
            return queryset.filter(owner__is_business=True)
        return queryset.filter(owner__is_business=False)
