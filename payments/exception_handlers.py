
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    APIException
)
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """هندلر سفارشی برای مدیریت خطاهای API"""
    
    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, Http404):
            exc = NotFound()
        elif isinstance(exc, ObjectDoesNotExist):
            exc = NotFound()
        else:
            logger.error(f"Unhandled exception: {exc}")
            exc = APIException(detail=_("خطای سرور رخ داده است"))
        response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'status_code': response.status_code,
            'message': '',
            'errors': {}
        }

        if isinstance(exc, ValidationError):
            error_data['message'] = _("داده‌های نامعتبر")
            error_data['errors'] = response.data

        elif isinstance(exc, AuthenticationFailed):
            error_data['message'] = _("احراز هویت ناموفق")
            error_data['errors'] = {'detail': str(exc)}

        elif isinstance(exc, NotAuthenticated):
            error_data['message'] = _("لطفا ابتدا وارد شوید")
            error_data['errors'] = {'detail': str(exc)}

        elif isinstance(exc, PermissionDenied):
            error_data['message'] = _("شما دسترسی لازم را ندارید")
            error_data['errors'] = {'detail': str(exc)}

        elif isinstance(exc, NotFound):
            error_data['message'] = _("مورد درخواستی یافت نشد")
            error_data['errors'] = {'detail': str(exc)}

        elif isinstance(exc, MethodNotAllowed):
            error_data['message'] = _("متد درخواستی مجاز نیست")
            error_data['errors'] = {'detail': str(exc)}

        else:
            error_data['message'] = _("خطایی رخ داده است")
            error_data['errors'] = {'detail': str(exc)}

        response.data = error_data

    return response

class PaymentError(APIException):
    """کلاس پایه برای خطاهای پرداخت"""
    status_code = 400
    default_detail = _("خطا در پرداخت")
    default_code = 'payment_error'

class PaymentInitError(PaymentError):
    """خطا در شروع پرداخت"""
    default_detail = _("خطا در شروع پرداخت")
    default_code = 'payment_init_error'

class PaymentVerifyError(PaymentError):
    """خطا در تایید پرداخت"""
    default_detail = _("خطا در تایید پرداخت")
    default_code = 'payment_verify_error'

class PaymentExpiredError(PaymentError):
    """خطای منقضی شدن پرداخت"""
    default_detail = _("پرداخت منقضی شده است")
    default_code = 'payment_expired'

class PaymentRefundError(PaymentError):
    """خطا در استرداد وجه"""
    default_detail = _("خطا در استرداد وجه")
    default_code = 'payment_refund_error'

class InvalidGatewayError(PaymentError):
    """خطای درگاه پرداخت نامعتبر"""
    default_detail = _("درگاه پرداخت نامعتبر است")
    default_code = 'invalid_gateway'
