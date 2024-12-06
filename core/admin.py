from django.contrib import admin
from django.utils.html import format_html
from .models import Property, PropertyImage

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="150" />', obj.image.url)
        return 'بدون تصویر'
    image_preview.short_description = 'پیش‌نمایش'

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'district', 'price_display', 'area', 'owner', 'created_at')
    list_filter = ('property_type', 'district', 'parking', 'elevator', 'created_at')
    search_fields = ('title', 'address', 'description', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PropertyImageInline]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': (
                ('title', 'property_type'),
                ('district', 'address'),
            )
        }),
        ('جزئیات قیمت و متراژ', {
            'fields': (
                ('price', 'area'),
                ('rooms', 'floor', 'total_floors'),
            )
        }),
        ('امکانات', {
            'fields': (
                ('parking', 'elevator'),
                ('storage', 'balcony'),
            )
        }),
        ('توضیحات', {
            'fields': ('description',)
        }),
        ('اطلاعات سیستمی', {
            'fields': ('owner', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def price_display(self, obj):
        return f"{obj.price:,} تومان"
    price_display.short_description = 'قیمت'

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'image_preview', 'is_main')
    list_filter = ('is_main', 'property__property_type')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return 'بدون تصویر'
    image_preview.short_description = 'تصویر'
