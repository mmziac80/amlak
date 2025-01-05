# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator

class PaymentAmountValidator:
    def __call__(self, value):
        MIN_AMOUNT = 50000  # حداقل 50 هزار تومان
        MAX_AMOUNT = 50000000  # حداکثر 50 میلیون تومان
        
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

class BankAccountValidator:
    def __call__(self, value):
        if not value.startswith('IR'):
            raise ValidationError(_('شماره شبا باید با IR شروع شود'))
            
        if len(value) != 26:
            raise ValidationError(_('شماره شبا باید 26 کاراکتر باشد'))
            
        if not value[2:].isdigit():
            raise ValidationError(_('شماره شبا باید فقط شامل اعداد باشد'))

class TrackingCodeValidator(RegexValidator):
    regex = r'^STL-[A-Z0-9]{8}$'
    message = _('کد پیگیری نامعتبر است')

class ReferenceIdValidator(RegexValidator):
    regex = r'^[A-Za-z0-9\-]{10,100}$'
    message = _('شناسه مرجع نامعتبر است')

def validate_settlement_date(value):
    """اعتبارسنجی تاریخ تسویه"""
    if value and value < timezone.now():
        raise ValidationError(
            _('تاریخ تسویه نمی‌تواند در گذشته باشد'),
            code='past_date'
        )

def validate_business_hours(value):
    """اعتبارسنجی ساعات کاری"""
    hour = value.hour
    if hour < 9 or hour > 17:
        raise ValidationError(
            _('تسویه فقط در ساعات کاری (9 تا 17) امکان‌پذیر است'),
            code='business_hours'
        )

def validate_working_day(value):
    """اعتبارسنجی روز کاری"""
    if value.weekday() in [4, 5]:  # پنجشنبه و جمعه
        raise ValidationError(
            _('تسویه در روزهای تعطیل امکان‌پذیر نیست'),
            code='working_day'
        )

def validate_owner_balance(user, amount):
    """اعتبارسنجی موجودی کاربر"""
    if user.balance < amount:
        raise ValidationError(
            _('موجودی کافی نیست'),
            code='insufficient_balance'
        )

