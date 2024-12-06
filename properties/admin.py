from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SaleProperty, 
    RentProperty, 
    DailyRentProperty, 
    Booking, 
    PropertyAvailability, 
    Visit,
    PropertyImage
)

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="150" />', obj.image.url)
        return 'بدون تصویر'
    image_preview.short_description = 'پیش‌نمایش'

@admin.register(SaleProperty)
class SalePropertyAdmin(admin.ModelAdmin):
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'property_type', 'price', 'price_per_meter')
        }),
        ('مشخصات', {
            'fields': ('area', 'rooms', 'floor', 'total_floors')
        }),
        ('امکانات', {
            'fields': ('parking', 'storage', 'elevator', 'balcony')
        }),
        ('موقعیت', {
            'fields': ('district', 'address', 'latitude', 'longitude')
        }),
    )
    list_display = ('title', 'property_type', 'price_display', 'price_per_meter', 'area', 'rooms')
    list_filter = ('property_type', 'district', 'parking', 'elevator')
    search_fields = ('title', 'description', 'address')
    inlines = [PropertyImageInline]

    def price_display(self, obj):
        return f"{obj.price:,} تومان"
    price_display.short_description = 'قیمت'

@admin.register(RentProperty)
class RentPropertyAdmin(admin.ModelAdmin):
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'property_type', 'deposit', 'rent')
        }),
        ('مشخصات', {
            'fields': ('area', 'rooms', 'floor', 'total_floors')
        }),
        ('موقعیت', {
            'fields': ('district', 'address', 'latitude', 'longitude')
        }),
        ('امکانات', {
            'fields': ('parking', 'storage', 'elevator', 'balcony')
        }),
    )
    list_display = ('title', 'property_type', 'deposit_display', 'rent_display', 'area', 'rooms')
    list_filter = ('property_type', 'district', 'parking', 'elevator')
    search_fields = ('title', 'description', 'address')
    inlines = [PropertyImageInline]

    def deposit_display(self, obj):
        return f"{obj.deposit:,} تومان"
    deposit_display.short_description = 'ودیعه'

    def rent_display(self, obj):
        return f"{obj.rent:,} تومان"
    rent_display.short_description = 'اجاره ماهانه'

@admin.register(DailyRentProperty)
class DailyRentPropertyAdmin(admin.ModelAdmin):
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'property_type', 'daily_price', 'images')
        }),
        ('مشخصات', {
            'fields': ('area', 'rooms', 'max_guests', 'min_stay', 'max_stay')
        }),
        ('امکانات', {
            'fields': ('wifi', 'tv', 'kitchen', 'washing_machine')
        }),
        ('موقعیت', {
            'fields': ('address', 'latitude', 'longitude')
        }),
    )
    list_display = ('title', 'property_type', 'daily_price_display', 'max_guests', 'area')
    list_filter = ('property_type', 'wifi', 'tv', 'kitchen')
    search_fields = ('title', 'description', 'address')
    inlines = [PropertyImageInline]

    def daily_price_display(self, obj):
        return f"{obj.daily_price:,} تومان"
    daily_price_display.short_description = 'قیمت روزانه'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'check_in', 'check_out', 'status', 'total_price_display')
    list_filter = ('status', 'check_in', 'check_out')
    search_fields = ('property__title', 'user__username')
    readonly_fields = ('created_at', 'payment_date')

    def total_price_display(self, obj):
        return f"{obj.total_price:,} تومان"
    total_price_display.short_description = 'مبلغ کل'

@admin.register(PropertyAvailability)
class PropertyAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('property', 'date', 'is_available', 'price_adjustment_display')
    list_filter = ('is_available', 'date')
    search_fields = ('property__title',)

    def price_adjustment_display(self, obj):
        return f"{obj.price_adjustment:,} تومان"
    price_adjustment_display.short_description = 'تعدیل قیمت'

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'visit_time', 'property', 'created_at', 'status')
    list_filter = ('visit_time', 'created_at', 'status')
    search_fields = ('name', 'phone', 'property__title')
