
from rest_framework import serializers
from .models import Payment, PaymentLog

class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    property_title = serializers.CharField(source='booking.property.title', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'amount', 'tracking_code',
            'status', 'status_display', 'property_title',
            'created_at'
        ]
        read_only_fields = ['tracking_code', 'status']

class PaymentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLog
        fields = ['id', 'payment', 'action', 'data', 'created_at']
        read_only_fields = ['created_at']
