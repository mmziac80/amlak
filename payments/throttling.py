
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .config import RATE_LIMIT_SETTINGS

class PaymentUserThrottle(UserRateThrottle):
    """محدودیت تعداد درخواست پرداخت برای کاربران"""
    scope = 'payment'
    rate = RATE_LIMIT_SETTINGS['PAYMENT_INIT_RATE']

class PaymentAnonThrottle(AnonRateThrottle):
    """محدودیت تعداد درخواست پرداخت برای کاربران مهمان"""
    scope = 'payment'
    rate = '5/hour'

class PaymentVerifyThrottle(UserRateThrottle):
    """محدودیت تعداد درخواست تایید پرداخت"""
    scope = 'payment_verify'
    rate = RATE_LIMIT_SETTINGS['PAYMENT_VERIFY_RATE']

class PaymentRefundThrottle(UserRateThrottle):
    """محدودیت تعداد درخواست استرداد"""
    scope = 'payment_refund' 
    rate = RATE_LIMIT_SETTINGS['PAYMENT_REFUND_RATE']

class ReportThrottle(UserRateThrottle):
    """محدودیت تعداد درخواست گزارش"""
    scope = 'report'
    rate = RATE_LIMIT_SETTINGS['REPORT_RATE']

class BurstRateThrottle(UserRateThrottle):
    """محدودیت تعداد درخواست در بازه کوتاه"""
    scope = 'burst'
    rate = '10/minute'

class SustainedRateThrottle(UserRateThrottle):
    """محدودیت تعداد درخواست در بازه طولانی"""
    scope = 'sustained'
    rate = '1000/day'

class IPRateThrottle(AnonRateThrottle):
    """محدودیت تعداد درخواست بر اساس IP"""
    scope = 'ip'
    rate = '1000/day'

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
