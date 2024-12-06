from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Property

@receiver(pre_save, sender=Property)
def calculate_price_per_meter(sender, instance, **kwargs):
    if instance.price and instance.area:
        instance.price_per_meter = instance.price / instance.area

@receiver(post_save, sender=Property)
def notify_new_property(sender, instance, created, **kwargs):
    if created:
        # ارسال نوتیفیکیشن برای املاک جدید
        pass
