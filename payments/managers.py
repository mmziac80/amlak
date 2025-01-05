# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.db.models import Sum, Count
from .constants import PAYMENT_STATUS

class PaymentManager(models.Manager):
    def pending(self):
        """برگرداندن پرداخت‌های در انتظار"""
        return self.filter(status=PAYMENT_STATUS['PENDING'])

    def successful(self):
        """برگرداندن پرداخت‌های موفق"""
        return self.filter(status=PAYMENT_STATUS['SUCCESS'])

    def failed(self):
        """برگرداندن پرداخت‌های ناموفق"""
        return self.filter(status=PAYMENT_STATUS['FAILED'])

    def expired(self):
        """برگرداندن پرداخت‌های منقضی شده"""
        return self.filter(status=PAYMENT_STATUS['EXPIRED'])

    def refunded(self):
        """برگرداندن پرداخت‌های مسترد شده"""
        return self.filter(status=PAYMENT_STATUS['REFUNDED'])

    def for_user(self, user):
        """برگرداندن پرداخت‌های یک کاربر"""
        return self.filter(user=user)

    def for_booking(self, booking):
        """برگرداندن پرداخت‌های یک رزرو"""
        return self.filter(booking=booking)

    def in_date_range(self, start_date, end_date):
        """برگرداندن پرداخت‌ها در یک بازه زمانی"""
        return self.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

    def total_amount(self, status=None):
        """محاسبه مجموع مبلغ پرداخت‌ها"""
        queryset = self.all()
        if status:
            queryset = queryset.filter(status=status)
        return queryset.aggregate(total=Sum('amount'))['total'] or 0

    def daily_stats(self, date=None):
        """آمار روزانه پرداخت‌ها"""
        date = date or timezone.now().date()
        return self.filter(created_at__date=date).aggregate(
            total_count=Count('id'),
            successful_count=Count('id', filter=models.Q(status=PAYMENT_STATUS['SUCCESS'])),
            total_amount=Sum('amount', filter=models.Q(status=PAYMENT_STATUS['SUCCESS']))
        )

class TransactionManager(models.Manager):
    def successful(self):
        """برگرداندن تراکنش‌های موفق"""
        return self.filter(status=PAYMENT_STATUS['SUCCESS'])

    def failed(self):
        """برگرداندن تراکنش‌های ناموفق"""
        return self.filter(status=PAYMENT_STATUS['FAILED'])

    def for_payment(self, payment):
        """برگرداندن تراکنش‌های یک پرداخت"""
        return self.filter(payment=payment)

    def in_date_range(self, start_date, end_date):
        """برگرداندن تراکنش‌ها در یک بازه زمانی"""
        return self.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

    def total_amount(self, status=None):
        """محاسبه مجموع مبلغ تراکنش‌ها"""
        queryset = self.all()
        if status:
            queryset = queryset.filter(status=status)
        return queryset.aggregate(total=Sum('amount'))['total'] or 0

    def daily_stats(self, date=None):
        """آمار روزانه تراکنش‌ها"""
        date = date or timezone.now().date()
        return self.filter(created_at__date=date).aggregate(
            total_count=Count('id'),
            successful_count=Count('id', filter=models.Q(status=PAYMENT_STATUS['SUCCESS'])),
            total_amount=Sum('amount', filter=models.Q(status=PAYMENT_STATUS['SUCCESS']))
        )
