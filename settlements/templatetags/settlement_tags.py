from django import template
from django.utils import timezone
from django.template.defaultfilters import floatformat
from ..models import Settlement

register = template.Library()

@register.filter
def status_color(status):
    """برگرداندن کلاس رنگ بوت‌استرپ بر اساس وضعیت تسویه"""
    colors = {
        'pending': 'warning',      # در انتظار - نارنجی
        'processing': 'info',      # در حال پردازش - آبی روشن
        'completed': 'success',    # تکمیل شده - سبز
        'failed': 'danger',        # ناموفق - قرمز
        'rejected': 'secondary',   # رد شده - خاکستری
        'cancelled': 'dark'        # لغو شده - مشکی
    }
    return colors.get(status, 'primary')

@register.filter
def time_since(value):
    """تبدیل تاریخ به زمان نسبی"""
    now = timezone.now()
    diff = now - value

    if diff.days > 365:
        years = diff.days // 365
        return f"{years} سال پیش"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} ماه پیش"
    elif diff.days > 0:
        return f"{diff.days} روز پیش"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} ساعت پیش"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} دقیقه پیش"
    else:
        return "لحظاتی پیش"

@register.filter
def currency(value):
    """نمایش مبلغ به فرمت پول"""
    try:
        value = float(value)
        return f"{floatformat(value, 0)} تومان"
    except (ValueError, TypeError):
        return value

@register.simple_tag
def settlement_status_badge(status):
    """نمایش نشان وضعیت با رنگ مناسب"""
    colors = {
        'pending': 'warning',
        'processing': 'info', 
        'completed': 'success',
        'failed': 'danger',
        'rejected': 'secondary',
        'cancelled': 'dark'
    }
    color = colors.get(status, 'primary')
    return f'<span class="badge bg-{color}">{status}</span>'

@register.filter
def progress_percentage(settlement):
    """محاسبه درصد پیشرفت تسویه"""
    status_weights = {
        'pending': 0,
        'processing': 50,
        'completed': 100,
        'failed': 100,
        'rejected': 100,
        'cancelled': 100
    }
    return status_weights.get(settlement.status, 0)

@register.filter
def amount_color(amount):
    """برگرداندن کلاس رنگ بر اساس مبلغ"""
    if amount >= 1000000:
        return 'text-success'
    elif amount >= 500000:
        return 'text-primary'
    return 'text-muted'

@register.filter
def processing_time(settlement):
    """محاسبه زمان پردازش تسویه به ساعت"""
    if settlement.settled_at and settlement.created_at:
        delta = settlement.settled_at - settlement.created_at
        hours = delta.total_seconds() / 3600
        return f"{hours:.1f} ساعت"
    return "-"

@register.filter
def bank_name(bank_account):
    """استخراج نام بانک از شماره شبا"""
    bank_codes = {
        '055': 'بانک اقتصاد نوین',
        '054': 'بانک پارسیان',
        '057': 'بانک پاسارگاد',
        '021': 'بانک ملی',
        '018': 'بانک تجارت',
        '015': 'بانک سپه',
        '016': 'بانک ملت',
        '017': 'بانک صادرات'
    }
    if bank_account.startswith('IR'):
        bank_code = bank_account[4:7]
        return bank_codes.get(bank_code, 'نامشخص')
    return 'نامشخص'
