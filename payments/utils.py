import logging
import requests
import json
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Sum
from kavenegar import KavenegarAPI

from .models import Payment, Transaction, RefundRequest
from .constants import (
    PAYMENT_STATUS,
    ZARINPAL,
    IDPAY,
    NEXTPAY,
    ERROR_CODES,
    SMS_TEMPLATES
)
from .exceptions import PaymentGatewayError, PaymentVerificationError

logger = logging.getLogger(__name__)

def init_payment(payment):
    """شروع فرآیند پرداخت"""
    try:
        if payment.gateway == 'zarinpal':
            return init_zarinpal_payment(payment)
        elif payment.gateway == 'idpay':
            return init_idpay_payment(payment)
        elif payment.gateway == 'nextpay':
            return init_nextpay_payment(payment)
        else:
            raise PaymentGatewayError('درگاه پرداخت نامعتبر است')
            
    except Exception as e:
        logger.error(f"Payment initialization failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def verify_payment(payment, authority):
    """تایید پرداخت"""
    try:
        if payment.gateway == 'zarinpal':
            return verify_zarinpal_payment(payment, authority)
        elif payment.gateway == 'idpay':
            return verify_idpay_payment(payment, authority)
        elif payment.gateway == 'nextpay':
            return verify_nextpay_payment(payment, authority)
        else:
            raise PaymentGatewayError('درگاه پرداخت نامعتبر است')
            
    except Exception as e:
        logger.error(f"Payment verification failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def send_payment_sms(mobile, message):
    """ارسال پیامک پرداخت"""
    try:
        api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
        params = {
            'receptor': mobile,
            'message': message
        }
        response = api.sms_send(params)
        return {'success': True, 'response': response}
    except Exception as e:
        logger.error(f"SMS sending failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def format_amount(amount):
    """فرمت‌بندی مبلغ"""
    return "{:,}".format(amount)

def get_payment_stats(user=None, start_date=None, end_date=None):
    """دریافت آمار پرداخت‌ها"""
    queryset = Payment.objects.all()
    
    if user:
        queryset = queryset.filter(user=user)
    if start_date:
        queryset = queryset.filter(created_at__gte=start_date)
    if end_date:
        queryset = queryset.filter(created_at__lte=end_date)

    stats = {
        'total_count': queryset.count(),
        'successful_count': queryset.filter(status=PAYMENT_STATUS['SUCCESS']).count(),
        'total_amount': queryset.filter(status=PAYMENT_STATUS['SUCCESS']).aggregate(
            total=Sum('amount')
        )['total'] or 0
    }
    
    stats['failed_count'] = stats['total_count'] - stats['successful_count']
    stats['success_rate'] = (
        (stats['successful_count'] / stats['total_count']) * 100 
        if stats['total_count'] > 0 else 0
    )
    
    return stats

def create_payment_transaction(payment, **kwargs):
    """ایجاد تراکنش جدید"""
    return Transaction.objects.create(
        payment=payment,
        amount=payment.amount,
        **kwargs
    )

def expire_pending_payments():
    """منقضی کردن پرداخت‌های معلق"""
    expiry_time = timezone.now() - timezone.timedelta(minutes=15)
    return Payment.objects.filter(
        status=PAYMENT_STATUS['PENDING'],
        created_at__lt=expiry_time
    ).update(status=PAYMENT_STATUS['EXPIRED'])

def cache_payment_status(payment_id, status, timeout=300):
    """ذخیره وضعیت پرداخت در کش"""
    cache_key = f'payment_status_{payment_id}'
    cache.set(cache_key, status, timeout)

def get_cached_payment_status(payment_id):
    """دریافت وضعیت پرداخت از کش"""
    cache_key = f'payment_status_{payment_id}'
    return cache.get(cache_key)

def process_refund_request(refund_request):
    """پردازش درخواست استرداد"""
    try:
        # اینجا کد مربوط به API بانک برای استرداد وجه قرار می‌گیرد
        refund_request.status = 'approved'
        refund_request.processed_at = timezone.now()
        refund_request.save()
        
        payment = refund_request.payment
        payment.status = PAYMENT_STATUS['REFUNDED']
        payment.save()
        
        return {'success': True}
        
    except Exception as e:
        logger.error(f"Refund processing failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def calculate_commission(amount, rate=0.1):
    """محاسبه کمیسیون"""
    return int(amount * rate)

def generate_tracking_code():
    """تولید کد پیگیری یکتا"""
    import uuid
    return str(uuid.uuid4().hex)[:10].upper()
