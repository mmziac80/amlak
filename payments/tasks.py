# -*- coding: utf-8 -*-
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Sum
import logging

from .models import Payment, RefundRequest
from .constants import PAYMENT_STATUS, PAYMENT_EXPIRY_MINUTES
from .utils import send_sms, call_bank_refund_api

logger = logging.getLogger(__name__)

def check_expired_payments():
    """بررسی و غیرفعال‌سازی پرداخت‌های منقضی شده"""
    expiry_time = timezone.now() - timezone.timedelta(minutes=PAYMENT_EXPIRY_MINUTES)
    
    expired_payments = Payment.objects.filter(
        Q(status=PAYMENT_STATUS['PENDING']) &
        Q(created_at__lt=expiry_time)
    )

    for payment in expired_payments:
        payment.status = PAYMENT_STATUS['EXPIRED']
        payment.save()

        # ارسال ایمیل به کاربر
        if payment.user.email:
            send_mail(
                subject='انقضای پرداخت',
                message=f'پرداخت شما با کد پیگیری {payment.tracking_code} منقضی شد.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[payment.user.email],
                fail_silently=True
            )

def send_payment_notification(mobile, message):
    """ارسال پیامک نوتیفیکیشن پرداخت"""
    return send_sms(mobile, message)

def process_refund(refund_request_id):
    """پردازش درخواست استرداد"""
    try:
        refund_request = RefundRequest.objects.get(id=refund_request_id)
        payment = refund_request.payment

        # شبیه‌سازی فراخوانی API بانک
        print(f"[DEBUG] Processing refund for payment {payment.id}")
        result = {'success': True}  # شبیه‌سازی پاسخ بانک

        if result['success']:
            refund_request.status = 'completed'
            refund_request.processed_at = timezone.now()
            refund_request.save()

            payment.status = PAYMENT_STATUS['REFUNDED']
            payment.save()

            if payment.user.email:
                send_mail(
                    subject='تایید استرداد وجه',
                    message=f'مبلغ {payment.amount:,} تومان به حساب شما واریز شد.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[payment.user.email],
                    fail_silently=True
                )

    except RefundRequest.DoesNotExist:
        logger.error(f"RefundRequest {refund_request_id} not found")

def generate_payment_report():
    """تولید گزارش روزانه پرداخت‌ها"""
    today = timezone.now().date()
    
    today_payments = Payment.objects.filter(created_at__date=today)
    
    successful = today_payments.filter(status=PAYMENT_STATUS['SUCCESS'])
    failed = today_payments.filter(status=PAYMENT_STATUS['FAILED'])
    expired = today_payments.filter(status=PAYMENT_STATUS['EXPIRED'])
    
    report = f"""گزارش پرداخت‌های {today}:
    
    تعداد کل: {today_payments.count()}
    موفق: {successful.count()}
    ناموفق: {failed.count()}
    منقضی شده: {expired.count()}
    
    جمع مبالغ موفق: {successful.aggregate(total=Sum('amount'))['total']:,} تومان
    """

    print(f"[DEBUG] Daily Report:\n{report}")  
    
    if settings.ADMINS:
        send_mail(
            subject=f'گزارش پرداخت‌های {today}',
            message=report,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin[1] for admin in settings.ADMINS],
            fail_silently=True
        )

def settle_with_owner(payment_id):
    """تسویه حساب با مالک - تسک celery"""
    try:
        payment = Payment.objects.get(id=payment_id)
        
        # شبیه‌سازی انتقال وجه
        print(f"[DEBUG] Simulating bank transfer for payment {payment_id}")
        bank_response = {'success': True, 'tracking_code': f"TEST-{payment_id}"}
        
        if bank_response['success']:
            payment.status = PAYMENT_STATUS['SETTLED']
            payment.settlement_date = timezone.now()
            payment.settlement_tracking_code = bank_response['tracking_code']
            payment.save()
            
            # ارسال پیامک به مالک
            send_sms(
                payment.owner.phone,
                f"مبلغ {payment.owner_amount:,} تومان بابت تسویه اجاره به حساب شما واریز شد."
            )
            
    except Payment.DoesNotExist:
        logger.error(f"Payment {payment_id} not found")

def sync_payment_statuses():
    """بروزرسانی وضعیت پرداخت‌ها از درگاه بانکی"""
    print("[DEBUG] Simulating payment status sync")
    pending_payments = Payment.objects.filter(
        status=PAYMENT_STATUS['PENDING'],
        created_at__gt=timezone.now() - timezone.timedelta(hours=24)
    )

    for payment in pending_payments:
        try:
            # شبیه‌سازی بررسی وضعیت
            print(f"[DEBUG] Checking status for payment {payment.id}")
            
        except Exception as e:
            logger.error(f"Error syncing payment {payment.id}: {str(e)}")
