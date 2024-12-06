from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Sum
import uuid

class Settlement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('processing', 'در حال پردازش'),
        ('completed', 'تسویه شده'),
        ('failed', 'ناموفق'),
        ('rejected', 'رد شده'),
        ('cancelled', 'لغو شده')
    ]

    tracking_code = models.CharField(
        max_length=32, 
        unique=True, 
        editable=False,
        verbose_name='کد پیگیری'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='settlements',
        verbose_name='مالک'
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        validators=[MinValueValidator(50000)],
        verbose_name='مبلغ'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='وضعیت'
    )
    bank_account = models.CharField(
        max_length=26,
        verbose_name='شماره شبا'
    )
    bank_reference_id = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='شناسه پیگیری بانکی'
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name='دلیل رد درخواست'
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_settlements',
        verbose_name='بررسی شده توسط'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )
    settled_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='تاریخ تسویه'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'تسویه حساب'
        verbose_name_plural = 'تسویه حساب‌ها'
        indexes = [
            models.Index(fields=['tracking_code']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['bank_reference_id'])
        ]

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = self.generate_tracking_code()
        super().save(*args, **kwargs)

    def generate_tracking_code(self):
        return f"STL-{uuid.uuid4().hex[:8].upper()}"

    def mark_as_completed(self, bank_reference_id, processed_by=None):
        self.status = 'completed'
        self.bank_reference_id = bank_reference_id
        self.settled_at = timezone.now()
        self.processed_by = processed_by
        self.save()

    def mark_as_failed(self, reason='', processed_by=None):
        self.status = 'failed'
        self.rejection_reason = reason
        self.processed_by = processed_by
        self.save()

    def mark_as_processing(self, processed_by=None):
        self.status = 'processing'
        self.processed_by = processed_by
        self.save()

    def mark_as_rejected(self, reason, processed_by=None):
        self.status = 'rejected'
        self.rejection_reason = reason
        self.processed_by = processed_by
        self.save()

    def mark_as_cancelled(self, reason='', processed_by=None):
        self.status = 'cancelled'
        self.rejection_reason = reason
        self.processed_by = processed_by
        self.save()

    def get_bank_name_from_sheba(self):
        bank_codes = {
            '055': 'بانک اقتصاد نوین',
            '054': 'بانک پارسیان',
            '057': 'بانک پاسارگاد',
            '058': 'بانک کارآفرین',
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
        if self.settled_at and self.created_at:
            return self.settled_at - self.created_at
        return None

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def is_failed(self):
        return self.status == 'failed'

    @property
    def waiting_days(self):
        if self.status == 'pending':
            return (timezone.now() - self.created_at).days
        return 0

    @classmethod
    def get_total_settled_amount(cls, owner=None):
        queryset = cls.objects.filter(status='completed')
        if owner:
            queryset = queryset.filter(owner=owner)
        result = queryset.aggregate(total=Sum('amount'))
        return result['total'] or 0

    def __str__(self):
        return f"Settlement {self.tracking_code} - {self.get_status_display()}"


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='کاربر'
    )
    action = models.CharField(
        max_length=50,
        verbose_name='عملیات'
    )
    object_id = models.IntegerField(
        null=True,
        verbose_name='شناسه شیء'
    )
    details = models.JSONField(
        null=True, 
        blank=True,
        verbose_name='جزئیات'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='آدرس IP'
    )
    user_agent = models.CharField(
        max_length=500,
        verbose_name='مرورگر کاربر'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان'
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'گزارش فعالیت'
        verbose_name_plural = 'گزارش‌های فعالیت'
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['ip_address'])
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
