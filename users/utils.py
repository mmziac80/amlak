import random
from django.utils import timezone
from datetime import timedelta

def generate_otp():
    return str(random.randint(100000, 999999))

def is_otp_valid(otp, stored_otp, expiry_time):
    if not stored_otp or not expiry_time:
        return False
    if timezone.now() > expiry_time:
        return False
    return otp == stored_otp

def send_sms(phone_number, message):
    """
    ارسال پیامک با استفاده از سرویس پیامک
    فعلا به صورت تستی پیاده‌سازی می‌شود
    """
    print(f"Sending SMS to {phone_number}: {message}")
    return True


