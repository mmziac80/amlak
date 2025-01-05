# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import User, UserActivity, UserProfile, UserNotification, UserDevice

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'پروفایل'
    verbose_name_plural = 'پروفایل'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        'username', 'get_full_name_display', 'phone',
        'email', 'get_status_display',
        'date_joined'
    )
    list_filter = (
        'is_active', 'is_staff',
        'is_superuser', 'date_joined'
    )
    search_fields = (
        'username', 'first_name', 'last_name',
        'email', 'phone', 'national_code'
    )
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {
            'fields': (
                'first_name', 'last_name', 'email',
                'phone', 'national_code', 'birth_date',
                'avatar', 'bank_account',
                'identity_verified', 'identity_document'
            )
        }),
        ('مجوزها و دسترسی‌ها', {
            'fields': (
                'is_active', 'is_phone_verified', 'is_staff',
                'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('تاریخ‌های مهم', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'phone', 'national_code',
                'password1', 'password2'
            ),
        }),
    )

    def get_full_name_display(self, obj):
        return obj.get_full_name()
    get_full_name_display.short_description = 'نام کامل'

    def get_status_display(self, obj):
        if obj.is_active:
            if obj.is_staff:
                return format_html('<span class="badge bg-success">مدیر</span>')
            elif obj.is_phone_verified:
                return format_html('<span class="badge bg-primary">فعال</span>')
            else:
                return format_html('<span class="badge bg-warning">در انتظار تایید</span>')
        return format_html('<span class="badge bg-danger">غیرفعال</span>')
    get_status_display.short_description = 'وضعیت'

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'activity_type', 'ip_address',
        'user_agent', 'created_at'
    )
    list_filter = ('activity_type', 'created_at')
    search_fields = (
        'user__username', 'user__phone',
        'ip_address', 'user_agent'
    )
    readonly_fields = (
        'user', 'activity_type', 'ip_address',
        'user_agent', 'created_at'
    )
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    ordering = ('-created_at',)
    
    class Meta:
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلان‌ها'

@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'is_active', 'last_login')
    list_filter = ('device_type', 'is_active')
    search_fields = ('user__username', 'device_id')
    ordering = ('-last_login',)
    
    class Meta:
        verbose_name = 'دستگاه'
        verbose_name_plural = 'دستگاه‌ها'

