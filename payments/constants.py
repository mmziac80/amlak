# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator

# مقادیر پایه پرداخت
MIN_PAYMENT_AMOUNT = 10000  
MAX_PAYMENT_AMOUNT = 100000000
PAYMENT_EXPIRY_MINUTES = 30

# وضعیت‌های پرداخت
PAYMENT_STATUS = {
    'PENDING': 'pending',
    'SUCCESS': 'success',
    'FAILED': 'failed',
    'REFUNDED': 'refunded',
    'EXPIRED': 'expired',
    'SETTLED': 'settled'
}

# نوع پرداخت
PAYMENT_TYPE = {
    'ONLINE': 'online',
    'CASH': 'cash',
    'CARD': 'card'
}

# درگاه‌های پرداخت
GATEWAY_CHOICES = [
    ('zarinpal', 'زرین‌پال'),
    ('idpay', 'آیدی پی'),
    ('nextpay', 'نکست پی')
]

# نرخ‌های کمیسیون
COMMISSION_RATES = {
    'DEFAULT': 0.10,  # 10%
    'SPECIAL': 0.08,  # 8%
    'VIP': 0.05      # 5%
}

# قالب پیامک‌ها
SMS_TEMPLATES = {
    'PAYMENT_SUCCESS': 'پرداخت شما با موفقیت انجام شد. کد پیگیری: {tracking_code}',
    'PAYMENT_FAILED': 'پرداخت ناموفق بود. لطفا مجددا تلاش کنید.',
    'SETTLEMENT_SUCCESS': 'مبلغ {amount} تومان به حساب شما واریز شد. کد پیگیری: {tracking_code}'
}

# تنظیمات درگاه زرین‌پال
ZARINPAL = {
    'MERCHANT': 'YOUR-ZARINPAL-MERCHANT-ID',
    'START_PAY_URL': 'https://www.zarinpal.com/pg/StartPay/',
    'API_URL': 'https://api.zarinpal.com/pg/v4/payment/',
    'CALLBACK_URL': 'http://localhost:8000/payments/callback/'
}

# تنظیمات درگاه آیدی پی
IDPAY = {
    'API_KEY': 'YOUR-IDPAY-API-KEY',
    'SANDBOX': True,  # تنظیم برای محیط تست
    'CALLBACK_URL': 'http://localhost:8000/payments/callback/',
    'API_URL': 'https://api.idpay.ir/v1.1/payment'
}

# تنظیمات درگاه نکست‌پی
NEXTPAY = {
    'API_KEY': 'YOUR-NEXTPAY-API-KEY',
    'SANDBOX': True,
    'CALLBACK_URL': 'http://localhost:8000/payments/callback/',
    'API_URL': 'https://nextpay.org/nx/gateway'
}

# کدهای خطای پرداخت
ERROR_CODES = {
    'INVALID_AMOUNT': 'مبلغ نامعتبر است',
    'INVALID_MERCHANT': 'کد پذیرنده نامعتبر است',
    'EXPIRED_PAYMENT': 'پرداخت منقضی شده است',
    'PAYMENT_FAILED': 'پرداخت ناموفق بود',
    'ALREADY_VERIFIED': 'تراکنش قبلا تایید شده است',
    'INVALID_AUTHORITY': 'کد مرجع نامعتبر است'
}

# Validators
class PaymentAmountValidator:
    """اعتبارسنجی مبلغ پرداخت"""
    def __call__(self, value):
        if value < MIN_PAYMENT_AMOUNT:
            raise ValidationError(
                _('مبلغ پرداخت نمی‌تواند کمتر از %(min)s تومان باشد'),
                params={'min': f"{MIN_PAYMENT_AMOUNT:,}"}
            )
        if value > MAX_PAYMENT_AMOUNT:
            raise ValidationError(
                _('مبلغ پرداخت نمی‌تواند بیشتر از %(max)s تومان باشد'),
                params={'max': f"{MAX_PAYMENT_AMOUNT:,}"}
            )

class TrackingCodeValidator(RegexValidator):
    """اعتبارسنجی کد پیگیری"""
    regex = r'^[A-Za-z0-9\-]{5,50}$'
    message = _('کد پیگیری باید شامل حروف، اعداد و خط تیره باشد (بین 5 تا 50 کاراکتر)')

class ShebaValidator(RegexValidator):
    """اعتبارسنجی شماره شبا"""
    regex = r'^IR[0-9]{24}$'
    message = _('شماره شبا باید با IR شروع شده و شامل 24 رقم باشد')

class BankAccountValidator(RegexValidator):
    """اعتبارسنجی شماره حساب بانکی"""
    regex = r'^[0-9]{9,16}$'
    message = _('شماره حساب باید بین 9 تا 16 رقم باشد')

def validate_payment_date(value):
    """اعتبارسنجی تاریخ پرداخت"""
    if value > timezone.now():
        raise ValidationError(_('تاریخ پرداخت نمی‌تواند در آینده باشد'))

def validate_mobile_number(value):
    """اعتبارسنجی شماره موبایل"""
    if not value.startswith('09'):
        raise ValidationError(_('شماره موبایل باید با 09 شروع شود'))
    if len(value) != 11:
        raise ValidationError(_('شماره موبایل باید 11 رقم باشد'))
    if not value.isdigit():
        raise ValidationError(_('شماره موبایل باید فقط شامل اعداد باشد'))

