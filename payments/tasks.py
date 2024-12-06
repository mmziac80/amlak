from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Sum

from .models import Payment, RefundRequest
from .constants import PAYMENT_STATUS, PAYMENT_EXPIRY_MINUTES
from .utils import send_sms, call_bank_refund_api

@shared_task
def check_expired_payments():
    """بررسی و به‌روزرسانی پرداخت‌های منقضی شده"""
    expiry_time = timezone.now() - timezone.timedelta(minutes=PAYMENT_EXPIRY_MINUTES)
    
    expired_payments = Payment.objects.filter(
        Q(status=PAYMENT_STATUS['PENDING']) &
        Q(created_at__lt=expiry_time)
    )

    for payment in expired_payments:
        payment.status = PAYMENT_STATUS['EXPIRED']
        payment.save()

        # ارسال ایمیل به کاربر
        send_mail(
            subject='انقضای پرداخت',
            message=f'پرداخت شما با کد پیگیری {payment.tracking_code} منقضی شد.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[payment.user.email],
            fail_silently=True
        )

@shared_task
def send_payment_notification(mobile, message):
    """ارسال پیامک اطلاع‌رسانی پرداخت"""
    return send_sms(mobile, message)

@shared_task
def process_refund(refund_request_id):
    """پردازش درخواست استرداد"""
    try:
        refund_request = RefundRequest.objects.get(id=refund_request_id)
        payment = refund_request.payment

        # فراخوانی API بانک برای استرداد
        result = call_bank_refund_api(
            amount=payment.amount,
            reference_id=payment.reference_id,
            sheba=refund_request.bank_account
        )

        if result['success']:
            refund_request.status = 'completed'
            refund_request.processed_at = timezone.now()
            refund_request.save()

            payment.status = PAYMENT_STATUS['REFUNDED']
            payment.save()

            # ارسال ایمیل تایید استرداد
            send_mail(
                subject='تایید استرداد وجه',
                message=f'مبلغ {payment.amount:,} تومان به حساب شما واریز شد.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[payment.user.email],
                fail_silently=True
            )

    except RefundRequest.DoesNotExist:
        pass

@shared_task
def generate_payment_report():
    """تولید گزارش روزانه پرداخت‌ها"""
    today = timezone.now().date()
    
    # آمار پرداخت‌های امروز
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

    # ارسال گزارش به ادمین‌ها
    send_mail(
        subject=f'گزارش پرداخت‌های {today}',
        message=report,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin[1] for admin in settings.ADMINS],
        fail_silently=True
    )

@shared_task
def settle_with_owner(payment_id):
    """تسویه حساب با مالک"""
    try:
        payment = Payment.objects.get(id=payment_id)
        
        # انتقال وجه به حساب مالک
        bank_response = call_bank_transfer_api(
            amount=payment.owner_amount,
            destination=payment.owner.bank_account,
            description=f"تسویه اجاره روزانه - کد {payment.bank_tracking_code}"
        )
        
        if bank_response['success']:
            payment.status = PAYMENT_STATUS['SETTLED']
            payment.settlement_date = timezone.now()
            payment.settlement_tracking_code = bank_response['tracking_code']
            payment.save()
            
            # ارسال پیامک به مالک
            send_sms(
                payment.owner.phone,
                f"مبلغ {payment.owner_amount:,} تومان بابت اجاره روزانه به حساب شما واریز شد."
            )
            
    except Payment.DoesNotExist:
        pass

@shared_task
def sync_payment_statuses():
    """همگام‌سازی وضعیت پرداخت‌ها با درگاه بانکی"""
    pending_payments = Payment.objects.filter(
        status=PAYMENT_STATUS['PENDING'],
        created_at__gt=timezone.now() - timezone.timedelta(hours=24)
    )

    for payment in pending_payments:
        try:
            # بررسی وضعیت در درگاه بانکی
            status = check_payment_status_in_bank(payment.reference_id)
            
            if status != payment.status:
                payment.status = status
                payment.save()
                
        except Exception as e:
            logger.error(f"Error syncing payment {payment.id}: {str(e)}")
