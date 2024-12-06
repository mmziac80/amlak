from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator

class PaymentAmountValidator:
    def __call__(self, value):
        MIN_AMOUNT = 10000  # حداقل 10 هزار تومان
        MAX_AMOUNT = 1000000000  # حداکثر یک میلیارد تومان
        
        if value < MIN_AMOUNT:
            raise ValidationError(
                _('مبلغ پرداخت نمی‌تواند کمتر از %(min)s تومان باشد'),
                params={'min': f"{MIN_AMOUNT:,}"}
            )
        if value > MAX_AMOUNT:
            raise ValidationError(
                _('مبلغ پرداخت نمی‌تواند بیشتر از %(max)s تومان باشد'),
                params={'max': f"{MAX_AMOUNT:,}"}
            )

class CommissionRateValidator:
    def __call__(self, value):
        if value < 0 or value > 1:
            raise ValidationError(_('نرخ کمیسیون باید بین 0 و 1 باشد'))

class TrackingCodeValidator(RegexValidator):
    regex = r'^[A-Za-z0-9\-]{5,50}'
    message = _('کد پیگیری باید شامل حروف، اعداد و خط تیره باشد')

class ReferenceIdValidator(RegexValidator):
    regex = r'^[A-Za-z0-9\-]{10,100}'
    message = _('شناسه مرجع باید شامل حروف، اعداد و خط تیره باشد')

class ShebaValidator(RegexValidator):
    regex = r'^IR[0-9]{24}'
    message = _('شماره شبا باید با IR شروع شده و شامل 24 رقم باشد')

class BankAccountValidator(RegexValidator):
    regex = r'^[0-9]{9,16}'
    message = _('شماره حساب باید بین 9 تا 16 رقم باشد')

def validate_payment_date(value):
    """اعتبارسنجی تاریخ پرداخت"""
    if value > timezone.now():
        raise ValidationError(
            _('تاریخ پرداخت نمی‌تواند در آینده باشد'),
            code='future_date'
        )

def validate_settlement_date(value):
    """اعتبارسنجی تاریخ تسویه"""
    if value and value < timezone.now():
        raise ValidationError(
            _('تاریخ تسویه نمی‌تواند در گذشته باشد'),
            code='past_date'
        )

def validate_mobile_number(value):
    """اعتبارسنجی شماره موبایل"""
    if not value.startswith('09'):
        raise ValidationError(
            _('شماره موبایل باید با 09 شروع شود'),
            code='invalid_prefix'
        )
    if len(value) != 11:
        raise ValidationError(
            _('شماره موبایل باید 11 رقم باشد'),
            code='invalid_length'
        )
    if not value.isdigit():
        raise ValidationError(
            _('شماره موبایل باید فقط شامل اعداد باشد'),
            code='invalid_chars'
        )

def validate_national_code(value):
    """اعتبارسنجی کد ملی"""
    if not value.isdigit() or len(value) != 10:
        raise ValidationError(_('کد ملی باید 10 رقم باشد'))
    
    check = int(value[9])
    s = sum(int(value[x]) * (10 - x) for x in range(9)) % 11
    if s < 2:
        control = s
    else:
        control = 11 - s
    if check != control:
        raise ValidationError(_('کد ملی نامعتبر است'))

def validate_card_number(value):
    """اعتبارسنجی شماره کارت بانکی"""
    if not value.isdigit() or len(value) != 16:
        raise ValidationError(_('شماره کارت باید 16 رقم باشد'))
    
    # الگوریتم Luhn
    s = 0
    for i in range(16):
        n = int(value[i])
        if i % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        s += n
    if s % 10 != 0:
        raise ValidationError(_('شماره کارت نامعتبر است'))
