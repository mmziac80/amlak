from django.core.cache import cache
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class BankService:
    def __init__(self):
        self.api_key = settings.PAYMENT_SETTINGS['MERCHANT_ID']
        self.base_url = 'https://api.bank.com/v1'  # آدرس تستی
        self.cache_timeout = 3600

    def transfer_to_owner(self, amount, destination, description):
        """انتقال وجه به حساب مالک - فعلا شبیه‌سازی شده"""
        try:
            print(f"Simulating bank transfer: Amount={amount}, To={destination}")
            return {
                'status': 'success',
                'tracking_code': '123456',
                'reference_id': 'REF123'
            }
        except Exception as e:
            logger.exception("Bank transfer failed")
            return {'status': 'failed', 'error': str(e)}

    def verify_transfer(self, tracking_code):
        """استعلام وضعیت انتقال - فعلا شبیه‌سازی شده"""
        print(f"Simulating transfer verification: {tracking_code}")
        return {'status': 'success'}

class SMSService:
    def __init__(self):
        self.api_key = settings.SMS_SETTINGS['API_KEY']
        self.sender = settings.SMS_SETTINGS['SENDER']
        self.is_fake = settings.SMS_SETTINGS['IS_FAKE']
        
    def send(self, phone, message):
        """ارسال پیامک"""
        try:
            if self.is_fake:
                # حالت تستی - نمایش در کنسول
                print(f"Sending SMS from {self.sender} to {phone}:")
                print(f"Message: {message}")
                return True
            else:
                # حالت واقعی - ارسال واقعی پیامک
                return self._send_real_sms(phone, message)
                
        except Exception as e:
            logger.exception("SMS sending failed")
            return False
            
    def _send_real_sms(self, phone, message):
        """ارسال واقعی پیامک - برای اتصال به سرویس"""
        try:
            # TODO: اتصال به API سرویس پیامک
            return True
        except Exception as e:
            logger.exception("Real SMS sending failed")
            return False

class EmailService:
    def send(self, to_email, subject, template, context):
        """ارسال ایمیل - نمایش در کنسول"""
        try:
            print(f"Sending email to {to_email}")
            print(f"Subject: {subject}")
            print(f"Context: {context}")
            return True
        except Exception as e:
            logger.exception("Email sending failed")
            return False
class NotificationService:
    def __init__(self):
        self.sms_service = SMSService()
        self.email_service = EmailService()

    def send_settlement_notification(self, user, amount, tracking_code):
        """ارسال نوتیفیکیشن تسویه به کاربر"""
        # ارسال پیامک
        sms_result = self._send_sms(
            phone=user.phone,
            message=self._get_settlement_sms_text(amount, tracking_code)
        )
        
        # ارسال ایمیل
        email_result = True
        if user.email:
            email_result = self._send_email(
                email=user.email,
                subject="تسویه حساب موفق",
                template="emails/settlement_success.html",
                context=self._get_settlement_email_context(user, amount, tracking_code)
            )
        
        return sms_result and email_result

    def _send_sms(self, phone, message):
        """فراخوانی از SMSService برای ارسال پیامک"""
        return self.sms_service.send(phone, message)

    def _send_email(self, email, subject, template, context):
        """فراخوانی از EmailService برای ارسال ایمیل"""
        return self.email_service.send(email, subject, template, context)

    def _get_settlement_sms_text(self, amount, tracking_code):
        return f"""تسویه حساب با موفقیت انجام شد
        مبلغ: {amount:,} تومان
        کد پیگیری: {tracking_code}"""

    def _get_settlement_email_context(self, user, amount, tracking_code):
        return {
            'user': user,
            'amount': amount,
            'tracking_code': tracking_code,
            'date': timezone.now()
        }