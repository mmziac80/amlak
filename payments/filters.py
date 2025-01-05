# -*- coding: utf-8 -*-

from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Payment, Transaction, RefundRequest
from .constants import PAYMENT_STATUS, PAYMENT_TYPE, GATEWAY_CHOICES

class PaymentFilter(filters.FilterSet):
    """فیلترهای پرداخت"""
    status = filters.ChoiceFilter(choices=[(k, v) for k, v in PAYMENT_STATUS.items()])
    payment_type = filters.ChoiceFilter(choices=[(k, v) for k, v in PAYMENT_TYPE.items()])
    gateway = filters.ChoiceFilter(choices=GATEWAY_CHOICES)

    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')

    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    booking_id = filters.NumberFilter(field_name='booking__id')
    property_id = filters.NumberFilter(field_name='booking__property__id')

    search = filters.CharFilter(method='search_filter')

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(tracking_code__icontains=value) |
            Q(reference_id__icontains=value) |
            Q(booking__property__title__icontains=value) |
            Q(user__username__icontains=value) |
            Q(user__mobile__icontains=value)
        )

    class Meta:
        model = Payment
        fields = [
            'status', 'payment_type', 'gateway',
            'min_amount', 'max_amount',
            'created_after', 'created_before',
            'booking_id', 'property_id'
        ]

class TransactionFilter(filters.FilterSet):
    """فیلترهای تراکنش"""
    status = filters.ChoiceFilter(choices=[(k, v) for k, v in PAYMENT_STATUS.items()])
    payment_id = filters.NumberFilter(field_name='payment__id')

    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')

    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    tracking_code = filters.CharFilter(lookup_expr='icontains')
    bank_reference_id = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Transaction
        fields = [
            'status', 'payment_id',
            'min_amount', 'max_amount',
            'created_after', 'created_before',
            'tracking_code', 'bank_reference_id'
        ]

class RefundRequestFilter(filters.FilterSet):
    """فیلترهای درخواست استرداد"""
    status = filters.ChoiceFilter(choices=[
        ('pending', 'در انتظار بررسی'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده')
    ])

    payment_id = filters.NumberFilter(field_name='payment__id')
    user_id = filters.NumberFilter(field_name='payment__user__id')

    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    processed_after = filters.DateTimeFilter(field_name='processed_at', lookup_expr='gte')
    processed_before = filters.DateTimeFilter(field_name='processed_at', lookup_expr='lte')

    min_amount = filters.NumberFilter(field_name='payment__amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='payment__amount', lookup_expr='lte')

    class Meta:
        model = RefundRequest
        fields = [
            'status', 'payment_id', 'user_id',
            'created_after', 'created_before',
            'processed_after', 'processed_before',
            'min_amount', 'max_amount'
        ]

