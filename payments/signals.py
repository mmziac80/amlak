from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache

from .models import Payment, Transaction, RefundRequest
from .utils import send_payment_sms
from .constants import PAYMENT_STATUS, SMS_TEMPLATES

@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    """سیگنال پس از ذخیره پرداخت"""
    if created:
        # ارسال پیامک شروع پرداخت
        send_payment_sms(
            instance.user.mobile,
            SMS_TEMPLATES['PAYMENT_SUCCESS'].format(
                tracking_code=instance.tracking_code
            )
        )
        
        # ذخیره در کش
        cache_key = f'payment_{instance.id}'
        cache.set(cache_key, instance.status, timeout=300)

@receiver(post_save, sender=Transaction) 
def transaction_post_save(sender, instance, created, **kwargs):
    """سیگنال پس از ذخیره تراکنش"""
    if created and instance.status == PAYMENT_STATUS['SUCCESS']:
        # بروزرسانی وضعیت پرداخت
        payment = instance.payment
        payment.status = PAYMENT_STATUS['SUCCESS']
        payment.save()

        # ارسال پیامک موفقیت تراکنش
        send_payment_sms(
            payment.user.mobile,
            SMS_TEMPLATES['PAYMENT_SUCCESS'].format(
                tracking_code=instance.tracking_code
            )
        )

@receiver(post_save, sender=RefundRequest)
def refund_request_post_save(sender, instance, created, **kwargs):
    """سیگنال پس از ذخیره درخواست استرداد"""
    if created:
        # ارسال پیامک ثبت درخواست
        send_payment_sms(
            instance.payment.user.mobile,
            SMS_TEMPLATES['REFUND_REQUEST'].format(
                tracking_code=instance.payment.tracking_code
            )
        )
    
    elif instance.status == 'approved':
        # ارسال پیامک تایید استرداد
        send_payment_sms(
            instance.payment.user.mobile,
            SMS_TEMPLATES['REFUND_SUCCESS'].format(
                amount=f"{instance.payment.amount:,}"
            )
        )

@receiver(pre_save, sender=Payment)
def payment_pre_save(sender, instance, **kwargs):
    """سیگنال پیش از ذخیره پرداخت"""
    if instance.status == PAYMENT_STATUS['SUCCESS']:
        # تنظیم تاریخ پرداخت موفق
        instance.paid_at = timezone.now()
    
    elif instance.status == PAYMENT_STATUS['EXPIRED']:
        # ارسال پیامک انقضای پرداخت
        send_payment_sms(
            instance.user.mobile,
            SMS_TEMPLATES['PAYMENT_EXPIRED']
        )
