# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
import uuid

class Settlement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('processing', 'در حال پردازش'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
        ('rejected', 'رد شده'),
        ('cancelled', 'لغو شده')
    ]

    tracking_code = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
        verbose_name=_('کد پیگیری')
    )
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='settlements',
        verbose_name=_('مالک')
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(50000)],
        verbose_name=_('مبلغ')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('وضعیت')
    )
    
    bank_account = models.CharField(
        max_length=26,
        verbose_name=_('شماره شبا')
    )
    
    bank_reference_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('شناسه پیگیری بانکی')
    )
    
    rejection_reason = models.TextField(
        blank=True,
        verbose_name=_('دلیل رد درخواست')
    )
    
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_settlements',
        verbose_name=_('بررسی شده توسط')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاریخ ایجاد')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاریخ بروزرسانی')
    )
    
    settled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاریخ تسویه')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('تسویه حساب')
        verbose_name_plural = _('تسویه حساب‌ها')
        indexes = [
            models.Index(fields=['tracking_code']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['bank_reference_id'])
        ]

    def __str__(self):
        return f"Settlement {self.tracking_code} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = self.generate_tracking_code()
        super().save(*args, **kwargs)

    def generate_tracking_code(self):
        """تولید کد پیگیری یکتا"""
        return f"STL-{uuid.uuid4().hex[:8].upper()}"

    def mark_as_completed(self, bank_reference_id, processed_by=None):
        """علامت‌گذاری به عنوان تکمیل شده"""
        self.status = 'completed'
        self.bank_reference_id = bank_reference_id
        self.settled_at = timezone.now()
        self.processed_by = processed_by
        self.save()

    def mark_as_failed(self, reason='', processed_by=None):
        """علامت‌گذاری به عنوان ناموفق"""
        self.status = 'failed'
        self.rejection_reason = reason
        self.processed_by = processed_by
        self.save()


    def mark_as_processing(self, processed_by=None):
        """علامت‌گذاری به عنوان در حال پردازش"""
        self.status = 'processing'
        self.processed_by = processed_by
        self.save()

    def mark_as_rejected(self, reason, processed_by=None):
        """علامت‌گذاری به عنوان رد شده"""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.processed_by = processed_by
        self.save()

    def mark_as_cancelled(self, reason='', processed_by=None):
        """علامت‌گذاری به عنوان لغو شده"""
        self.status = 'cancelled'
        self.rejection_reason = reason
        self.processed_by = processed_by
        self.save()

    def get_bank_name_from_sheba(self):
        """دریافت نام بانک از شماره شبا"""
        bank_codes = {
            '055': 'بانک اقتصاد نوین',
            '054': 'بانک پارسیان',
            '057': 'بانک پاسارگاد',
            '058': 'بانک سینا',
            '051': 'بانک ملت',
            '016': 'بانک ملی ایران',
            '062': 'بانک آینده',
            '053': 'بانک تجارت',
            '069': 'بانک صادرات',
            '056': 'بانک سامان'
        }
        if self.bank_account.startswith('IR'):
            bank_code = self.bank_account[4:7]
            return bank_codes.get(bank_code, 'نامشخص')
        return 'نامشخص'

    @property
    def processing_time(self):
        """محاسبه زمان پردازش درخواست"""
        if self.settled_at and self.created_at:
            return self.settled_at - self.created_at
        return None

    @property
    def is_pending(self):
        """بررسی در انتظار بودن درخواست"""
        return self.status == 'pending'

    @property
    def is_completed(self):
        """بررسی تکمیل شدن درخواست"""
        return self.status == 'completed'

    @property
    def is_failed(self):
        """بررسی ناموفق بودن درخواست"""
        return self.status == 'failed'

    @property
    def waiting_days(self):
        """محاسبه روزهای انتظار درخواست"""
        if self.status == 'pending':
            return (timezone.now() - self.created_at).days
        return 0

    @classmethod
    def get_total_settled_amount(cls, owner=None):
        """محاسبه مجموع تسویه حساب‌های موفق"""
        queryset = cls.objects.filter(status='completed')
        if owner:
            queryset = queryset.filter(owner=owner)
        result = queryset.aggregate(total=Sum('amount'))
        return result['total'] or 0


class AuditLog(models.Model):
    """ثبت لاگ تغییرات سیستم"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('کاربر')
    )
    
    action = models.CharField(
        max_length=50,
        verbose_name=_('عملیات')
    )
    
    object_id = models.IntegerField(
        null=True,
        verbose_name=_('شناسه شیء')
    )
    
    details = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('جزئیات')
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name=_('آدرس IP')
    )
    
    user_agent = models.CharField(
        max_length=500,
        verbose_name=_('مرورگر کاربر')
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('زمان')
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('گزارش تغییرات')
        verbose_name_plural = _('گزارش‌های تغییرات')
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['ip_address'])
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"

    
