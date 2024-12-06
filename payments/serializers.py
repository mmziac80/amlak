from rest_framework import serializers
from django.utils import timezone
from django.conf import settings
from decimal import Decimal

from .models import Payment, Transaction, RefundRequest, Property
from .constants import PAYMENT_STATUS, PAYMENT_TYPE, GATEWAY_CHOICES
from .validators import (
    PaymentAmountValidator,
    TrackingCodeValidator,
    ReferenceIdValidator,
    ShebaValidator
)

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

class CommissionRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'commission_rate']
        
    def validate_commission_rate(self, value):
        if value < settings.COMMISSION_SETTINGS['MIN_RATE']:
            raise serializers.ValidationError(f"نرخ کمیسیون نمی‌تواند کمتر از {settings.COMMISSION_SETTINGS['MIN_RATE']} باشد")
        if value > settings.COMMISSION_SETTINGS['MAX_RATE']:
            raise serializers.ValidationError(f"نرخ کمیسیون نمی‌تواند بیشتر از {settings.COMMISSION_SETTINGS['MAX_RATE']} باشد")
        return value

class PaymentSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    renter_name = serializers.CharField(source='renter.get_full_name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'property', 'property_title',
            'renter', 'renter_name',
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
    bank_account = serializers.CharField(validators=[ShebaValidator()])

class PaymentStatusSerializer(serializers.ModelSerializer):
    """سریالایزر وضعیت پرداخت"""
    class Meta:
        model = Payment
        fields = [
            'id', 'status', 'tracking_code',
            'reference_id', 'amount', 'created_at'
        ]
        validators = [TrackingCodeValidator(), ReferenceIdValidator()]

class PaymentReportSerializer(serializers.Serializer):
    """سریالایزر گزارش پرداخت"""
    total_count = serializers.IntegerField()
    successful_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=0)
    average_amount = serializers.DecimalField(max_digits=12, decimal_places=0)
    success_rate = serializers.FloatField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['total_amount'] = f"{int(data['total_amount']):,}"
        data['average_amount'] = f"{int(data['average_amount']):,}"
        data['success_rate'] = f"{data['success_rate']:.1f}%"
        return data

class BulkCommissionUpdateSerializer(serializers.Serializer):
    property_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    commission_rate = serializers.DecimalField(
        max_digits=4,
        decimal_places=2
    )
