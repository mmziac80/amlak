# -*- coding: utf-8 -*-

from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from .models import Settlement
from .logging import SettlementLogger, AuditLogger

@receiver(pre_save, sender=Settlement)
def log_settlement_status_change(sender, instance, **kwargs):
    """ثبت تغییرات وضعیت تسویه"""
    if instance.id:
        old_instance = Settlement.objects.get(id=instance.id)
        if old_instance.status != instance.status:
            SettlementLogger.log_settlement_status_change(
                settlement=instance,
                old_status=old_instance.status,
                new_status=instance.status
            )

@receiver(post_save, sender=Settlement)
def log_settlement_creation(sender, instance, created, **kwargs):
    """ثبت ایجاد تسویه جدید"""
    if created:
        SettlementLogger.log_settlement_creation(instance)

@receiver(post_save, sender=Settlement)
def update_user_balance(sender, instance, created, **kwargs):
    """بروزرسانی موجودی کاربر"""
    if instance.status == 'completed':
        with transaction.atomic():
            user = instance.owner
            user.balance -= instance.amount
            user.save()

@receiver(post_save, sender=Settlement)
def clear_user_settlements_cache(sender, instance, **kwargs):
    """پاک کردن کش تسویه‌های کاربر"""
    cache.delete(f'user_settlements_{instance.owner.id}')
    cache.delete('total_settlements_stats')

@receiver(pre_delete, sender=Settlement)
def log_settlement_deletion(sender, instance, **kwargs):
    """ثبت حذف تسویه"""
    SettlementLogger.log_settlement_deletion(instance)

@receiver(post_save, sender=Settlement)
def notify_admin_large_settlement(sender, instance, created, **kwargs):
    """اطلاع‌رسانی به ادمین برای تسویه‌های با مبلغ بالا"""
    if created and instance.amount >= 10000000:  # مبالغ بالای 10 میلیون تومان
        SettlementLogger.log_large_settlement(instance)

@receiver(post_save, sender=Settlement)
def track_settlement_timing(sender, instance, created, **kwargs):
    """ثبت زمان‌بندی تسویه"""
    if instance.status == 'completed':
        processing_time = timezone.now() - instance.created_at
        SettlementLogger.log_settlement_timing(instance, processing_time)

