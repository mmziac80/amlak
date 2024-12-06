from django.core.cache import cache
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from tenacity import retry, stop_after_attempt, wait_exponential
from django_ratelimit.decorators import ratelimit
import requests
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class BankService:
    def __init__(self):
        self.api_key = settings.BANK_API_KEY
        self.base_url = settings.BANK_API_URL
        self.cache_timeout = 3600  # 1 hour

    @ratelimit(key='ip', rate='100/h')
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def transfer_to_owner(self, amount, destination, description):
        """انتقال وجه به حساب مالک"""
        self._validate_transfer_input(amount, destination)
        
        try:
            response = requests.post(
                f"{self.base_url}/transfer/",
                json={
                    'amount': amount,
                    'destination': destination,
                    'description': description
                },
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self._cache_transfer_result(data)
                return {
                    'status': 'success',
                    'tracking_code': data['tracking_code'],
                    'reference_id': data['reference_id']
                }
                
            logger.error(f"Bank transfer failed: {response.text}")
            return {'status': 'failed', 'error': 'خطا در انتقال وجه'}
            
        except Exception as e:
            logger.exception("Bank transfer exception")
            return {'status': 'failed', 'error': str(e)}

    def verify_transfer(self, tracking_code):
        """استعلام وضعیت انتقال وجه"""
        cache_key = f'transfer_status_{tracking_code}'
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        try:
            response = requests.get(
                f"{self.base_url}/verify/{tracking_code}/",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                cache.set(cache_key, result, self.cache_timeout)
                return result
                
            return {'status': 'failed'}
            
        except Exception as e:
            logger.exception("Bank verify exception")
            return {'status': 'failed'}

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def _validate_transfer_input(self, amount, destination):
        if not isinstance(amount, (int, float, Decimal)) or amount <= 0:
            raise ValueError("مبلغ نامعتبر است")
        if not destination or len(destination) < 10:
            raise ValueError("شماره حساب مقصد نامعتبر است")

    def _cache_transfer_result(self, data):
        cache_key = f"transfer_{data['tracking_code']}"
        cache.set(cache_key, data, self.cache_timeout)

class NotificationService:
    def send_settlement_notification(self, user, amount, tracking_code):
        """ارسال نوتیفیکیشن تسویه به کاربر"""
        notifications = []
        
        # ارسال پیامک
        sms_result = self.send_sms(
            phone=user.phone,
            message=self._get_settlement_sms_text(amount, tracking_code)
        )
        notifications.append(('sms', sms_result))
        
        # ارسال ایمیل
        email_result = self.send_email(
            email=user.email,
            subject="تسویه حساب موفق",
            template="emails/settlement_success.html",
            context=self._get_settlement_email_context(user, amount, tracking_code)
        )
        notifications.append(('email', email_result))
        
        # ذخیره نوتیفیکیشن
        self._save_notification(user, amount, tracking_code)
        
        return all(result for _, result in notifications)

    def bulk_send_sms(self, messages):
        """ارسال گروهی پیامک"""
        sms_service = SMSService()
        results = []
        
        for phone, message in messages:
            result = sms_service.send(phone, message)
            results.append((phone, result))
            
        return results

    def bulk_send_email(self, emails):
        """ارسال گروهی ایمیل"""
        email_service = EmailService()
        results = []
        
        for email_data in emails:
            result = email_service.send(**email_data)
            results.append((email_data['email'], result))
            
        return results

    def _get_settlement_sms_text(self, amount, tracking_code):
        return f"""تسویه حساب با موفقیت انجام شد
        مبلغ: {amount:,} تومان
        کد پیگیری: {tracking_code}"""

    def _get_settlement_email_context(self, user, amount, tracking_code):
        return {
            'user': user,
            'amount': amount,
            'tracking_code': tracking_code
        }

    def _save_notification(self, user, amount, tracking_code):
        Notification.objects.create(
            user=user,
            title="تسویه حساب",
            message=f"تسویه حساب به مبلغ {amount:,} تومان با موفقیت انجام شد",
            type="settlement",
            reference_code=tracking_code
        )

class SMSService:
    def __init__(self):
        self.api_key = settings.SMS_API_KEY
        self.sender = settings.SMS_SENDER
        self.base_url = settings.SMS_API_URL

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def send(self, phone, message):
        try:
            response = requests.post(
                f"{self.base_url}/send/",
                json={
                    'receptor': phone,
                    'message': message,
                    'sender': self.sender
                },
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            return response.status_code == 200
        except Exception as e:
            logger.exception("SMS sending failed")
            return False

class EmailService:
    @retry(stop=stop_after_attempt(3))
    def send(self, email, subject, template, context):
        try:
            html_message = render_to_string(template, context)
            send_mail(
                subject=subject,
                message=strip_tags(html_message),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message
            )
            return True
        except Exception as e:
            logger.exception("Email sending failed")
            return False
