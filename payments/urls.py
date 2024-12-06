from celery import shared_task
from django.utils import timezone
from django.conf import settings
from .models import Payment
from .utils import send_sms

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60 * 60  # 1 hour
)
def settle_with_owner(self, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        
        # بررسی وضعیت پرداخت
        if payment.status != 'paid':
            return False
            
        # انتقال وجه به حساب مالک
        bank_response = transfer_to_owner_account(
            amount=payment.owner_amount,
            destination=payment.owner.bank_account,
            description=f"تسویه اجاره روزانه - کد {payment.tracking_code}"
        )
        
        if bank_response['status'] == 'success':
            # بروزرسانی وضعیت تسویه
            payment.settlement_status = 'settled'
            payment.settlement_date = timezone.now()
            payment.settlement_tracking_code = bank_response['tracking_code']
            payment.save()
            
            # ارسال پیامک به مالک
            send_settlement_notification(payment)
            return True
            
        else:
            raise Exception(f"خطا در انتقال وجه: {bank_response['message']}")
            
    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        raise exc

@shared_task
def send_settlement_notification(payment):
    message = f"""تسویه حساب اجاره روزانه:
    مبلغ: {payment.owner_amount} تومان
    کد پیگیری: {payment.settlement_tracking_code}
    """
    send_sms(payment.owner.phone, message)

def transfer_to_owner_account(amount, destination, description):
    """
    پیاده‌سازی اتصال به API بانک و انتقال وجه
    """
    # در اینجا کد اتصال به API بانک قرار می‌گیرد
    return {
        'status': 'success',
        'tracking_code': 'SETTLE-123456'
    }
