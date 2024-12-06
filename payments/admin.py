from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Payment, Transaction, Settlement, Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'owner', 'commission_rate_display', 
        'daily_price_display', 'created_at'
    ]
    list_editable = ['commission_rate']
    list_filter = ['commission_rate', 'created_at']
    search_fields = ['title', 'owner__username', 'owner__phone']
    
    def commission_rate_display(self, obj):
        return f'{obj.commission_rate}%'
    commission_rate_display.short_description = 'نرخ کمیسیون'
    
    def daily_price_display(self, obj):
        return format_html(
            '<span style="color: green;">{:,} تومان</span>',
            obj.daily_price
        )
    daily_price_display.short_description = 'قیمت روزانه'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'tracking_code', 'property', 'renter', 'owner',
        'total_amount_display', 'commission_amount_display',
        'owner_amount_display', 'payment_status', 'settlement_status'
    ]
    list_filter = [
        'payment_status', 'settlement_status', 
        'created_at', 'payment_date'
    ]
    search_fields = [
        'tracking_code', 'payment_tracking_code',
        'renter__username', 'renter__phone',
        'owner__username', 'owner__phone',
        'property__title'
    ]
    readonly_fields = [
        'tracking_code', 'commission_amount', 
        'owner_amount', 'settlement_date'
    ]
    
    def total_amount_display(self, obj):
        return format_html(
            '<span style="color: green;">{:,} تومان</span>',
            obj.total_amount
        )
    total_amount_display.short_description = 'مبلغ کل'

    def commission_amount_display(self, obj):
        return format_html(
            '<span style="color: blue;">{:,} تومان</span>',
            obj.commission_amount
        )
    commission_amount_display.short_description = 'کمیسیون'

    def owner_amount_display(self, obj):
        return format_html(
            '<span style="color: purple;">{:,} تومان</span>',
            obj.owner_amount
        )
    owner_amount_display.short_description = 'سهم مالک'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'tracking_code', 'payment', 'amount_display',
        'transaction_type', 'status', 'created_at'
    ]
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = [
        'tracking_code', 'payment__tracking_code',
        'bank_tracking_code'
    ]
    readonly_fields = ['tracking_code', 'bank_tracking_code']

    def amount_display(self, obj):
        return format_html(
            '<span style="color: green;">{:,} تومان</span>',
            obj.amount
        )
    amount_display.short_description = 'مبلغ'

@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = [
        'tracking_code', 'owner', 'amount_display',
        'status', 'created_at', 'settled_at'
    ]
    list_filter = ['status', 'created_at', 'settled_at']
    search_fields = [
        'tracking_code', 'owner__username',
        'owner__phone', 'bank_tracking_code'
    ]
    readonly_fields = ['tracking_code', 'settled_at']
    actions = ['mark_as_settled', 'mark_as_failed']

    def amount_display(self, obj):
        return format_html(
            '<span style="color: green;">{:,} تومان</span>',
            obj.amount
        )
    amount_display.short_description = 'مبلغ'

    def mark_as_settled(self, request, queryset):
        queryset.update(
            status='settled',
            settled_at=timezone.now()
        )
    mark_as_settled.short_description = 'علامت‌گذاری به عنوان تسویه شده'

    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
    mark_as_failed.short_description = 'علامت‌گذاری به عنوان ناموفق'
