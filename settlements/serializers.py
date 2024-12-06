from rest_framework import serializers
from django.utils import timezone
from django.db.models import Avg
from .models import Settlement
from .validators import (
    PaymentAmountValidator, 
    BankAccountValidator,
    TrackingCodeValidator
)

class SettlementSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    waiting_days = serializers.SerializerMethodField()
    
    class Meta:
        model = Settlement
        fields = [
            'id', 'tracking_code', 'owner', 'owner_name',
            'amount', 'status', 'status_display', 'waiting_days',
            'bank_account', 'created_at', 'settled_at'
        ]
        read_only_fields = ['tracking_code', 'settled_at', 'waiting_days']

    def get_waiting_days(self, obj):
        if obj.status == 'pending':
            delta = timezone.now() - obj.created_at
            return delta.days
        return 0

class SettlementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settlement
        fields = ['amount', 'bank_account']
        validators = [PaymentAmountValidator(), BankAccountValidator()]

    def validate_amount(self, value):
        min_amount = 50000  # حداقل ۵۰ هزار تومان
        max_amount = 50000000  # حداکثر ۵۰ میلیون تومان
        
        if value < min_amount:
            raise serializers.ValidationError(f'حداقل مبلغ تسویه {min_amount:,} تومان است')
        if value > max_amount:
            raise serializers.ValidationError(f'حداکثر مبلغ تسویه {max_amount:,} تومان است')
            
        return value

    def validate_bank_account(self, value):
        if not value.startswith('IR'):
            raise serializers.ValidationError('شماره شبا باید با IR شروع شود')
        return value

class SettlementStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    bank_tracking_code = serializers.CharField(read_only=True)
    
    class Meta:
        model = Settlement
        fields = [
            'id', 'tracking_code', 'status', 'status_display',
            'amount', 'created_at', 'settled_at', 'bank_tracking_code'
        ]

class SettlementDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    owner_phone = serializers.CharField(source='owner.phone', read_only=True)
    bank_name = serializers.SerializerMethodField()
    processing_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Settlement
        fields = [
            'id', 'tracking_code', 'owner', 'owner_name',
            'owner_phone', 'amount', 'status', 'status_display',
            'bank_account', 'bank_name', 'created_at', 'settled_at',
            'rejection_reason', 'bank_reference_id', 'processing_time'
        ]

    def get_bank_name(self, obj):
        return obj.get_bank_name_from_sheba()

    def get_processing_time(self, obj):
        if obj.settled_at and obj.created_at:
            delta = obj.settled_at - obj.created_at
            return f"{delta.total_seconds() / 3600:.1f} ساعت"
        return None

class SettlementReportSerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    successful_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=0)
    average_amount = serializers.DecimalField(max_digits=12, decimal_places=0)
    success_rate = serializers.FloatField()
    recent_settlements = SettlementSerializer(many=True)
    average_processing_time = serializers.FloatField()
    daily_settlement_counts = serializers.DictField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['total_amount'] = f"{int(data['total_amount']):,}"
        data['average_amount'] = f"{int(data['average_amount']):,}"
        data['success_rate'] = f"{data['success_rate']:.1f}%"
        data['average_processing_time'] = f"{data['average_processing_time']:.1f} ساعت"
        return data

class SettlementFilterSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    status = serializers.ChoiceField(choices=Settlement.STATUS_CHOICES, required=False)
    min_amount = serializers.IntegerField(required=False)
    max_amount = serializers.IntegerField(required=False)
    owner_id = serializers.IntegerField(required=False)
    tracking_code = serializers.CharField(required=False, validators=[TrackingCodeValidator()])

    def validate(self, data):
        if data.get('date_from') and data.get('date_to'):
            if data['date_from'] > data['date_to']:
                raise serializers.ValidationError('تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد')
                
        if data.get('min_amount') and data.get('max_amount'):
            if data['min_amount'] > data['max_amount']:
                raise serializers.ValidationError('حداقل مبلغ نمی‌تواند بیشتر از حداکثر مبلغ باشد')
                
        return data
