# -*- coding: utf-8 -*-

from rest_framework import serializers
from payments.models import Payment
from properties.models import Property
from django.utils import timezone

class CreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['property', 'total_amount']

    def validate_property(self, value):
        if value.listing_type != 'daily':
            raise serializers.ValidationError("فقط املاک اجاره روزانه قابل پرداخت هستند")
        if not value.is_available:
            raise serializers.ValidationError("این ملک در تاریخ انتخابی قابل رزرو نیست")
        return value

    def validate_total_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("مبلغ پرداختی باید بیشتر از صفر باشد")
        return value

    def create(self, validated_data):
        validated_data['renter'] = self.context['request'].user
        validated_data['owner'] = validated_data['property'].owner
        validated_data['payment_status'] = 'pending'
        payment = Payment.objects.create(**validated_data)
        payment.calculate_amounts()
        return payment

class PaymentSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'property', 'property_title', 'total_amount',
            'payment_status', 'status_display', 'payment_date',
            'bank_tracking_code'
        ]
        read_only_fields = [
            'payment_status', 'payment_date', 'bank_tracking_code',
            'commission_amount'
        ]

class PaymentDetailSerializer(PaymentSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    owner_phone = serializers.CharField(source='owner.phone', read_only=True)
    renter_name = serializers.CharField(source='renter.get_full_name', read_only=True)
    
    class Meta(PaymentSerializer.Meta):
        fields = PaymentSerializer.Meta.fields + [
            'owner_name', 'owner_phone', 'renter_name',
            'commission_amount', 'owner_amount', 
            'settlement_date', 'settlement_tracking_code'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # فقط برای پرداخت‌های موفق اطلاعات تماس نمایش داده شود
        if instance.payment_status != 'paid':
            data.pop('owner_phone', None)
        return data

class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'total_amount', 'payment_status',
            'payment_date', 'bank_tracking_code'
        ]

