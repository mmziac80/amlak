# -*- coding: utf-8 -*-

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Property, SaleProperty

@receiver(pre_save, sender=Property)
def calculate_price_per_meter(sender, instance, **kwargs):
    # بررسی نوع ملک و محاسبه قیمت بر متر
    if hasattr(instance, 'saleproperty'):
        sale_property = instance.saleproperty
        if sale_property.price and instance.area:
            sale_property.price_per_meter = sale_property.price / instance.area

@receiver(post_save, sender=Property)
def notify_new_property(sender, instance, created, **kwargs):
    if created:
        # اینجا می‌توانیم نوتیفیکیشن‌های مختلف را بر اساس نوع ملک ارسال کنیم
        property_type = None
        if hasattr(instance, 'saleproperty'):
            property_type = 'sale'
        elif hasattr(instance, 'rentproperty'):
            property_type = 'rent'
        elif hasattr(instance, 'dailyrentproperty'):
            property_type = 'daily'
            
        # اینجا می‌توانید کد ارسال نوتیفیکیشن را اضافه کنید
        # مثال:
        # send_notification(
        #     title=f"ملک جدید: {instance.title}",
        #     type=property_type
        # )
