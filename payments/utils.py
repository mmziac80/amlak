# -*- coding: utf-8 -*-
import logging
import requests
import json
import uuid
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Sum

from .models import Payment, Transaction, RefundRequest
from .constants import PAYMENT_STATUS
from .exceptions import PaymentGatewayError, PaymentVerificationError

logger = logging.getLogger(__name__)

# کلاس‌های مربوط به SMS
class SMSProvider:
    """کلاس پایه برای ارائه‌دهندگان SMS"""
    def send(self, phone, message):
        raise NotImplementedError

class FakeSMSProvider(SMSProvider):
    """ارائه‌دهنده تستی SMS"""
    def send(self, phone, message):
        print(f"[FAKE SMS] To: {phone}")
        print(f"Message: {message}")
        return True

class KavenegarSMSProvider(SMSProvider):
    """ارائه‌دهنده کاوه‌نگار - برای استفاده در آینده"""
    def send(self, phone, message):
        try:
            # TODO: پیاده‌سازی در آینده
            print(f"[KAVENEGAR] Would send to {phone}: {message}")
            return True
        except Exception as e:
            logger.error(f"Kavenegar SMS failed: {str(e)}")
            return False

def get_sms_provider():
    """برگرداندن ارائه‌دهنده SMS بر اساس تنظیمات"""
    if settings.SMS_SETTINGS.get('IS_FAKE', True):
        return FakeSMSProvider()
    return KavenegarSMSProvider()

def send_sms(phone, message):
    """تابع اصلی ارسال پیامک"""
    try:
        provider = get_sms_provider()
        return provider.send(phone, message)
    except Exception as e:
        logger.error(f"SMS sending failed: {str(e)}")
        return False

# توابع مربوط به پرداخت
def init_payment(payment):
    """شروع فرآیند پرداخت"""
    try:
        response = requests.post(settings.PAYMENT_GATEWAY['REQUEST_URL'], {
            'merchant_id': settings.PAYMENT_GATEWAY['MERCHANT_ID'],
            'amount': payment.amount,
            'callback_url': settings.PAYMENT_GATEWAY['CALLBACK_URL'],
            'description': f'پرداخت شماره {payment.id}'
        })
        
        result = response.json()
        if result['status'] == 100:
            return {'success': True, 'token': result['token']}
            
        return {'success': False, 'error': result['message']}
            
    except Exception as e:
        logger.error(f"Payment initialization failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def verify_payment(payment, authority):
    """تایید پرداخت"""
    try:
        response = requests.post(settings.PAYMENT_GATEWAY['VERIFY_URL'], {
            'merchant_id': settings.PAYMENT_GATEWAY['MERCHANT_ID'],
            'authority': authority,
            'amount': payment.amount
        })
        
        result = response.json()
        if result['status'] == 100:
            return {'success': True, 'ref_id': result['ref_id']}
            
        return {'success': False, 'error': result['message']}
        
    except Exception as e:
        logger.error(f"Payment verification failed: {str(e)}")
        return {'success': False, 'error': str(e)}

# سایر توابع کمکی
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

# توابع مربوط به تراکنش‌ها
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

# توابع مربوط به کش
def cache_payment_status(payment_id, status, timeout=300):
    """ذخیره وضعیت پرداخت در کش"""
    cache_key = f'payment_status_{payment_id}'
    cache.set(cache_key, status, timeout)

def get_cached_payment_status(payment_id):
    """دریافت وضعیت پرداخت از کش"""
    cache_key = f'payment_status_{payment_id}'
    return cache.get(cache_key)

# توابع مربوط به استرداد و کمیسیون
def process_refund_request(refund_request):
    """پردازش درخواست استرداد"""
    try:
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
    return str(uuid.uuid4().hex)[:10].upper()

def call_bank_refund_api(payment, amount):
    """فراخوانی API بانک برای استرداد وجه"""
    try:
        # TODO: پیاده‌سازی اتصال به API بانک
        print(f"Calling bank refund API for payment {payment.id}, amount: {amount}")
        return True
        
    except Exception as e:
        logger.error(f"Bank refund API call failed: {str(e)}")
        return False

