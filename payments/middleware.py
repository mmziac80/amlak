# -*- coding: utf-8 -*-

from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from .models import Payment
from .constants import PAYMENT_STATUS, PAYMENT_EXPIRY_MINUTES

class PaymentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # بررسی و به‌روزرسانی پرداخت‌های منقضی شده
        if request.user.is_authenticated:
            expiry_time = timezone.now() - timezone.timedelta(minutes=PAYMENT_EXPIRY_MINUTES)
            expired_payments = Payment.objects.filter(
                user=request.user,
                status=PAYMENT_STATUS['PENDING'],
                created_at__lt=expiry_time
            )
        
            if expired_payments.exists():
                expired_payments.update(status=PAYMENT_STATUS['EXPIRED'])
                messages.warning(
                    request,
                    'برخی از پرداخت‌های شما به دلیل عدم تکمیل منقضی شده‌اند'
                )

        response = self.get_response(request)
        return response

class PaymentVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # بررسی وضعیت پرداخت در صفحات نیازمند پرداخت
        if request.path.startswith('/properties/daily/'):
            booking_id = request.resolver_match.kwargs.get('booking_id')
            if booking_id:
                payment = Payment.objects.filter(
                    booking_id=booking_id,
                    status=PAYMENT_STATUS['SUCCESS']
                ).exists()
            
                if not payment and not request.path.startswith('/payment/'):
                    messages.warning(
                        request,
                        'لطفاً ابتدا پرداخت را تکمیل کنید'
                    )
                    return redirect('payment_init', booking_id=booking_id)

        response = self.get_response(request)
        return response

