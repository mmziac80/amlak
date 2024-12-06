from functools import wraps
from django.core.cache import cache
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status

from .models import Payment
from .constants import PAYMENT_STATUS
from .exceptions import PaymentError, PaymentExpiredError

def check_payment_status(view_func):
    """بررسی وضعیت پرداخت"""
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        payment_id = kwargs.get('pk')
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id)
                if payment.status != PAYMENT_STATUS['PENDING']:
                    return Response(
                        {'error': 'این پرداخت قابل پردازش نیست'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Payment.DoesNotExist:
                return Response(
                    {'error': 'پرداخت یافت نشد'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return view_func(self, request, *args, **kwargs)
    return wrapper

def cache_payment_response(timeout=300):
    """کش کردن پاسخ API پرداخت"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            cache_key = f"payment_response_{kwargs.get('pk')}"
            response = cache.get(cache_key)
            if response is None:
                response = view_func(self, request, *args, **kwargs)
                cache.set(cache_key, response, timeout)
            return response
        return wrapper
    return decorator

def validate_payment_ownership(view_func):
    """بررسی مالکیت پرداخت"""
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        payment_id = kwargs.get('pk')
        if payment_id:
            payment = Payment.objects.get(id=payment_id)
            if payment.user != request.user:
                return Response(
                    {'error': 'شما دسترسی به این پرداخت ندارید'},
                    status=status.HTTP_403_FORBIDDEN
                )
        return view_func(self, request, *args, **kwargs)
    return wrapper

def check_payment_expiry(view_func):
    """بررسی انقضای پرداخت"""
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        payment_id = kwargs.get('pk')
        if payment_id:
            payment = Payment.objects.get(id=payment_id)
            if payment.expired_at and payment.expired_at < timezone.now():
                return Response(
                    {'error': 'پرداخت منقضی شده است'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return view_func(self, request, *args, **kwargs)
    return wrapper

def require_payment_verification(view_func):
    """نیاز به تایید پرداخت"""
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        payment_id = kwargs.get('pk')
        if payment_id:
            payment = Payment.objects.get(id=payment_id)
            if payment.status != PAYMENT_STATUS['SUCCESS']:
                return Response(
                    {'error': 'پرداخت هنوز تایید نشده است'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return view_func(self, request, *args, **kwargs)
    return wrapper

def track_payment_metrics(view_func):
    """ثبت متریک‌های پرداخت"""
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        response = view_func(self, request, *args, **kwargs)
        payment_id = kwargs.get('pk')
        if payment_id:
            cache.incr(f'payment_views_{payment_id}')
        return response
    return wrapper