# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import models
from django.forms import widgets
from django.conf import settings
from django.utils.html import format_html
from django import forms
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin


from typing import Any, Type
from django.forms import ModelForm




from .models import (
    Property,
    PropertyImage,
    SaleProperty,
    RentProperty,
    DailyRentProperty,
    PropertyFeature,
    Visit  
)


class PropertyAdminForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = '__all__'


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

class BasePropertyAdmin(LeafletGeoAdmin):
    map_template = 'properties/admin/gis/neshan_map.html'


    map_width = '100%'
    map_height = '500px'
        # تنظیمات ویجت نقشه
    settings_overrides = {
        'DEFAULT_CENTER': (36.2972, 59.6067),  # مختصات مشهد
        'DEFAULT_ZOOM': 14,
        'TILES': [],  # خالی چون نشان خودش تایل‌ها را مدیریت می‌کند
        'SCALE': True,  # نمایش مقیاس
        'MINIMAP': True,  # نمایش نقشه کوچک
    }
    form = PropertyAdminForm
    list_filter = ['status', 'is_active', 'is_featured']
    search_fields = ['title', 'description', 'address']

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'property_type')
        }),
        ('موقعیت مکانی و آدرس', {
            'fields': ('location', 'district', 'address'),
            'classes': ('location-fieldset',),
            'description': 'موقعیت ملک را روی نقشه انتخاب کنید'
        }),

        ('مشخصات ملک', {
            'fields': ('area', 'rooms', 'floor', 'total_floors', 'build_year')
        }),
        ('امکانات', {
            'fields': ('parking', 'elevator', 'storage', 'balcony', 'package',
                      'security', 'pool', 'gym', 'renovation')
        }),
    )
    class Media:
        css = {
            'all': (
                'https://static.neshan.org/sdk/leaflet/v1.9.4/neshan-sdk/v1.0.8/index.css',
            )
        }
        js = [
            'https://static.neshan.org/sdk/leaflet/v1.9.4/neshan-sdk/v1.0.8/index.js',
        ]







    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form


    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)

    def add_view(self, request: HttpRequest, form_url: str = '', extra_context=None):
        User = get_user_model()
        data = request.POST.copy()
        
        # تبدیل ID کاربر به string
        data['owner'] = str(request.user.pk)
        
        request.POST = data
        return super().add_view(request, form_url, extra_context)

@admin.register(Property)
class PropertyAdmin(BasePropertyAdmin):
    inlines = [PropertyImageInline]
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            if hasattr(obj, 'saleproperty'):
                return SalePropertyAdmin.form
            elif hasattr(obj, 'rentproperty'):
                return RentPropertyAdmin.form
            elif hasattr(obj, 'dailyrentproperty'):
                return DailyRentPropertyAdmin.form
        return form
@admin.register(SaleProperty)
class SalePropertyAdmin(BasePropertyAdmin):
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'property_type')
        }),
        ('موقعیت مکانی و آدرس', {
            'fields': ('location', 'district', 'address'),
            'classes': ('location-fieldset',),
            'description': 'موقعیت ملک را روی نقشه انتخاب کنید یا آدرس را وارد کنید'
        }),
        ('مشخصات ملک', {
            'fields': ('area', 'rooms', 'floor', 'total_floors', 'build_year')
        }),
        ('امکانات', {
            'fields': ('parking', 'elevator', 'storage', 'balcony', 'package',
                      'security', 'pool', 'gym', 'renovation')
        }),
        ('قیمت و شرایط فروش', {
            'fields': ('total_price', 'price_per_meter', 'is_exchangeable',
                      'is_negotiable', 'exchange_description')
        }),
        ('وضعیت', {
            'fields': ('status', 'is_featured', 'is_active')
        })
    )
    list_display = ('title', 'total_price', 'area', 'status', 'is_active', 'created_at', 'property_type', 'district')
    list_filter = list(BasePropertyAdmin.list_filter) + ['property_type', 'district']


    inlines = [PropertyImageInline]
@admin.register(RentProperty)
class RentPropertyAdmin(BasePropertyAdmin):
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'property_type')
        }),
        ('موقعیت مکانی و آدرس', {
            'fields': ('location', 'district', 'address'),
            'classes': ('location-fieldset',),
            'description': 'موقعیت ملک را روی نقشه انتخاب کنید یا آدرس را وارد کنید'
        }),
        ('مشخصات ملک', {
            'fields': ('area', 'rooms', 'floor', 'total_floors', 'build_year')
        }),
        ('امکانات', {
            'fields': ('parking', 'elevator', 'storage', 'balcony', 'package',
                      'security', 'pool', 'gym', 'renovation')
        }),
        ('شرایط اجاره', {
            'fields': ('monthly_rent', 'deposit', 'is_convertible',
                      'minimum_lease', 'has_transfer_fee')
        }),
        ('وضعیت', {
            'fields': ('status', 'is_featured', 'is_active')
        })
    )
    list_display = ('title', 'monthly_rent', 'deposit', 'area', 'status', 'is_active', 'created_at', 'property_type', 'district')
    list_filter = list(BasePropertyAdmin.list_filter) + ['property_type', 'district']


    inlines = [PropertyImageInline]

@admin.register(DailyRentProperty)
class DailyRentPropertyAdmin(BasePropertyAdmin):
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'property_type')  # Added deal_type
        }),
        ('موقعیت مکانی و آدرس', {
            'fields': ('location', 'district', 'address'),
            'classes': ('location-fieldset',),
            'description': 'موقعیت ملک را روی نقشه انتخاب کنید یا آدرس را وارد کنید'
        }),
        ('مشخصات ملک', {
            'fields': ('area', 'rooms', 'floor', 'total_floors', 'build_year')
        }),
        ('امکانات', {
            'fields': ('parking', 'elevator', 'storage', 'balcony', 'package',
                      'security', 'pool', 'gym', 'renovation')
        }),
        ('شرایط اقامت', {
            'fields': ('daily_price', 'min_stay', 'maximum_days', 'max_guests',
                      'extra_person_fee', 'check_in_time', 'check_out_time')
        }),
        ('وضعیت', {
            'fields': ('status', 'is_featured', 'is_active')
        })
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if form and hasattr(form, 'instance'):
            form.instance.deal_type = 'daily'
        return form




    def save_model(self, request, obj, form, change):
        obj.deal_type = 'daily'  # Always set deal_type to 'daily'
        super().save_model(request, obj, form, change)

    list_display = ('title', 'daily_price', 'area', 'status', 'is_active', 'created_at', 'property_type', 'district')
    list_filter = list(BasePropertyAdmin.list_filter) + ['property_type', 'district']

    inlines = [PropertyImageInline]

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ['property', 'visitor', 'visit_date', 'visit_time', 'status', 'created_at']
    list_filter = ['status', 'visit_date', 'created_at']
    search_fields = ['property__title', 'visitor__username', 'notes']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('اطلاعات بازدید', {
            'fields': ('property', 'visitor', 'visit_date', 'visit_time')
        }),
        ('وضعیت', {
            'fields': ('status', 'notes')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
