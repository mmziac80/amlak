# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Settlement, AuditLog

@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = [
        'tracking_code', 'owner', 'amount_display',
        'status', 'created_at', 'settled_at'
    ]
    list_filter = ['status', 'created_at', 'settled_at']
    search_fields = [
        'tracking_code', 'owner__username',
        'owner__phone', 'bank_reference_id'
    ]
    readonly_fields = ['tracking_code', 'settled_at']
    actions = ['mark_as_completed', 'mark_as_failed']

    def amount_display(self, obj):
        return format_html(
            '<span style="color: green;">{:,} تومان</span>',
            obj.amount
        )
    amount_display.short_description = 'مبلغ'

    def mark_as_completed(self, request, queryset):
        queryset.update(
            status='completed',
            settled_at=timezone.now()
        )
    mark_as_completed.short_description = 'علامت‌گذاری به عنوان تسویه شده'

    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
    mark_as_failed.short_description = 'علامت‌گذاری به عنوان ناموفق'

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'timestamp']
    list_filter = ['action', 'timestamp', 'ip_address']
    search_fields = ['user__username', 'action', 'ip_address', 'details']
    readonly_fields = ['user', 'action', 'object_id', 'details', 'ip_address', 'user_agent', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            search_term_as_int = int(search_term)
            queryset |= self.model.objects.filter(object_id=search_term_as_int)
        except ValueError:
            pass
        return queryset, use_distinct

