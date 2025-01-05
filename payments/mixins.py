# -*- coding: utf-8 -*-

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from rest_framework import status
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone

from .models import Payment, Transaction
from .constants import PAYMENT_STATUS
from .exceptions import PaymentError, PaymentExpiredError

class PaymentRequiredMixin(LoginRequiredMixin):
    """میکسین بررسی وضعیت پرداخت"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        booking_id = kwargs.get('booking_id')
        if booking_id:
            payment_exists = Payment.objects.filter(
                booking_id=booking_id,
                status=PAYMENT_STATUS['SUCCESS']
            ).exists()
        
            if not payment_exists:
                messages.warning(request, 'لطفا ابتدا پرداخت را انجام دهید')
                return redirect('payments:payment_init', booking_id=booking_id)
            
        return super().dispatch(request, *args, **kwargs)

class PaymentOwnershipMixin:
    """میکسین بررسی مالکیت پرداخت"""

    def dispatch(self, request, *args, **kwargs):
        payment_id = kwargs.get('payment_id')
        if payment_id:
            payment = Payment.objects.get(id=payment_id)
            if payment.user != request.user:
                messages.error(request, 'شما دسترسی به این پرداخت ندارید')
                return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class PaymentCacheMixin:
    """میکسین برای مدیریت کش پرداخت"""

    def get_cache_key(self, payment_id):
        return f'payment_status_{payment_id}'
    
    def get_cached_status(self, payment_id):
        return cache.get(self.get_cache_key(payment_id))
    
    def set_cached_status(self, payment_id, status, timeout=300):
        cache.set(self.get_cache_key(payment_id), status, timeout)

class PaymentValidationMixin:
    """میکسین برای اعتبارسنجی پرداخت"""

    def validate_payment(self, payment):
        if payment.status != PAYMENT_STATUS['PENDING']:
            raise PaymentError('این پرداخت قابل پردازش نیست')
        
        if payment.is_expired:
            raise PaymentExpiredError()
        
        return True

class TransactionCreateMixin:
    """میکسین برای ایجاد تراکنش"""

    def create_transaction(self, payment, **kwargs):
        return Transaction.objects.create(
            payment=payment,
            amount=payment.amount,
            **kwargs
        )

class PaymentCallbackMixin:
    """میکسین برای پردازش بازگشت از درگاه"""

    def handle_successful_payment(self, payment, ref_id):
        payment.status = PAYMENT_STATUS['SUCCESS']
        payment.reference_id = ref_id
        payment.save()
    
        self.create_transaction(
            payment=payment,
            status=PAYMENT_STATUS['SUCCESS'],
            bank_reference_id=ref_id
        )
    
        return Response({
            'status': 'success',
            'ref_id': ref_id
        })
    
    def handle_failed_payment(self, payment, error):
        payment.status = PAYMENT_STATUS['FAILED']
        payment.save()
    
        self.create_transaction(
            payment=payment,
            status=PAYMENT_STATUS['FAILED']
        )
    
        return Response({
            'status': 'failed',
            'error': str(error)
        }, status=status.HTTP_400_BAD_REQUEST)

class PaymentReportMixin:
    """میکسین برای گزارش‌گیری پرداخت"""

    def get_payment_stats(self, queryset):
        total = queryset.count()
        successful = queryset.filter(status=PAYMENT_STATUS['SUCCESS']).count()
    
        return {
            'total': total,
            'successful': successful,
            'failed': total - successful,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }

class PaymentRefundMixin:
    """میکسین برای استرداد پرداخت"""

    def validate_refund(self, payment):
        if not payment.can_request_refund:
            raise PaymentError('این پرداخت قابل استرداد نیست')
        
        if payment.has_refund_request:
            raise PaymentError('درخواست استرداد قبلاً ثبت شده است')
        
        return True
    
    def process_refund(self, payment, bank_account):
        payment.status = PAYMENT_STATUS['REFUNDED']
        payment.refund_bank_account = bank_account
        payment.refunded_at = timezone.now()
        payment.save()
    
        self.create_transaction(
            payment=payment,
            status=PAYMENT_STATUS['REFUNDED'],
            amount=payment.amount
        )
