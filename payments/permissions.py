# -*- coding: utf-8 -*-

from rest_framework import permissions
from .models import Payment
from .constants import PAYMENT_STATUS

class IsPaymentOwner(permissions.BasePermission):
    """مجوز دسترسی به پرداخت فقط برای صاحب آن"""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class CanInitiatePayment(permissions.BasePermission):
    """مجوز شروع پرداخت جدید"""

    def has_permission(self, request, view):
        booking_id = view.kwargs.get('booking_id')
        if booking_id:
            # بررسی عدم وجود پرداخت موفق قبلی برای این رزرو
            return not Payment.objects.filter(
                booking_id=booking_id,
                status=PAYMENT_STATUS['SUCCESS']
            ).exists()
        return True

class CanVerifyPayment(permissions.BasePermission):
    """مجوز تایید پرداخت"""

    def has_object_permission(self, request, view, obj):
        return (
            obj.user == request.user and 
            obj.status == PAYMENT_STATUS['PENDING']
        )

class CanRefundPayment(permissions.BasePermission):
    """مجوز درخواست استرداد"""

    def has_object_permission(self, request, view, obj):
        return (
            obj.user == request.user and
            obj.status == PAYMENT_STATUS['SUCCESS'] and
            obj.can_request_refund
        )

class CanViewPaymentHistory(permissions.BasePermission):
    """مجوز مشاهده تاریخچه پرداخت‌ها"""

    def has_permission(self, request, view):
        return request.user.is_authenticated

class IsPaymentAdmin(permissions.BasePermission):
    """مجوز دسترسی ادمین به پرداخت‌ها"""

    def has_permission(self, request, view):
        return request.user.is_staff

class CanAccessReport(permissions.BasePermission):
    """مجوز دسترسی به گزارش‌ها"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_staff or request.user.has_perm('payments.view_report'))
        )

class IsVerifiedUser(permissions.BasePermission):
    """مجوز دسترسی کاربران تایید شده"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_verified
        )

class CanManageRefunds(permissions.BasePermission):
    """مجوز مدیریت درخواست‌های استرداد"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.has_perm('payments.manage_refunds')
        )

