# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from .models import Payment, Transaction, RefundRequest, Property
from .constants import PAYMENT_STATUS, PAYMENT_TYPE, GATEWAY_CHOICES
class TransactionSerializer(serializers.ModelSerializer):
    """سریالایزر تراکنش‌ها"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'payment', 'amount', 'status', 'status_display',
            'tracking_code', 'bank_reference_id', 'created_at'
        ]
        read_only_fields = [
            'tracking_code', 'bank_reference_id', 'created_at'
        ]

class PaymentSerializer(serializers.ModelSerializer):
    """سریالایزر پرداخت"""
    property_title = serializers.CharField(source='property.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'property', 'property_title',
            'user', 'user_name',
            'owner', 'owner_name',
            'total_amount', 'commission_rate',
            'commission_amount', 'owner_amount',
            'payment_status', 'settlement_status',
            'payment_date', 'settlement_date',
            'payment_tracking_code', 'settlement_tracking_code',
            'created_at'
        ]
        read_only_fields = [
            'commission_amount', 'owner_amount',
            'payment_date', 'settlement_date',
            'payment_tracking_code', 'settlement_tracking_code'
        ]

class PaymentInitSerializer(serializers.Serializer):
    """سریالایزر شروع پرداخت"""
    property_id = serializers.IntegerField()
    payment_type = serializers.ChoiceField(choices=PAYMENT_TYPE.items())
    gateway = serializers.ChoiceField(choices=GATEWAY_CHOICES)
    callback_url = serializers.URLField()

class PaymentVerifySerializer(serializers.Serializer):
    """سریالایزر تایید پرداخت"""
    authority = serializers.CharField()
    status = serializers.CharField()

class PaymentRefundSerializer(serializers.Serializer):
    """سریالایزر درخواست استرداد"""
    reason = serializers.CharField(max_length=500)
    bank_account = serializers.CharField()

class PaymentDetailSerializer(serializers.ModelSerializer):
    """سریالایزر جزئیات پرداخت"""
    property_title = serializers.CharField(source='property.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'property', 'property_title',
            'user', 'user_name',
            'owner', 'owner_name',
            'total_amount', 'status', 'status_display',
            'created_at', 'payment_date',
            'tracking_code', 'reference_id'
        ]

class RefundRequestSerializer(serializers.ModelSerializer):
    """سریالایزر درخواست استرداد وجه"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    payment_amount = serializers.DecimalField(source='payment.total_amount', max_digits=12, decimal_places=0, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = RefundRequest
        fields = [
            'id', 'payment', 'payment_amount',
            'user', 'user_name',
            'reason', 'bank_account',
            'status', 'status_display',
            'created_at'
        ]
        read_only_fields = ['status', 'created_at']
