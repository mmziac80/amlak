# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
import random
from .services import BankService, NotificationService
from django.contrib.auth import get_user_model

User = get_user_model()

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'مسترد شده')
]

    SETTLEMENT_STATUS = [
       ('pending', 'در انتظار تسویه'),
       ('processing', 'در حال تسویه'),
       ('completed', 'تسویه شده'),
       ('failed', 'تسویه ناموفق')
]
      # ????????
    property = models.ForeignKey(
          'properties.Property', 
          on_delete=models.PROTECT, 
          related_name='payments',
          verbose_name=_('ملک')
      )
    user = models.ForeignKey(
          settings.AUTH_USER_MODEL,
          related_name='payments',
          on_delete=models.PROTECT,
          verbose_name=_('?????')
      )
    owner = models.ForeignKey(
          settings.AUTH_USER_MODEL,
          related_name='received_payments',
          on_delete=models.PROTECT,
          verbose_name=_('کاربر')
      )
    # ?????
    total_amount = models.DecimalField(
        _('مبلغ کل'),
        max_digits=12,
        decimal_places=0
    )
    commission_rate = models.DecimalField(
        _('نرخ کمیسیون'),
        max_digits=4,
        decimal_places=2,
        validators=[
            MinValueValidator(settings.COMMISSION_SETTINGS['MIN_RATE']),
            MaxValueValidator(settings.COMMISSION_SETTINGS['MAX_RATE'])
        ]
    )
    commission_amount = models.DecimalField(
        _('مبلغ کمیسیون'),
        max_digits=12,
        decimal_places=0
    )
    owner_amount = models.DecimalField(
        _('سهم مالک'),
        max_digits=12,
        decimal_places=0
    )

    # وضعیت‌ها
    payment_status = models.CharField(
        _('وضعیت پرداخت'),
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending'
    )
    settlement_status = models.CharField(
        _('وضعیت تسویه'),
        max_length=20,
        choices=SETTLEMENT_STATUS,
        default='pending'
    )

    # تاریخ‌ها
    check_in_date = models.DateField(_('تاریخ ورود'))
    check_out_date = models.DateField(_('تاریخ خروج'))
    payment_date = models.DateTimeField(_('تاریخ پرداخت'), null=True, blank=True)
    settlement_date = models.DateTimeField(_('تاریخ تسویه'), null=True, blank=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    # ????? ??????
    tracking_code = models.CharField(
        _('کد پیگیری'),
        max_length=50,
        unique=True,
        editable=False
    )
    payment_tracking_code = models.CharField(
         _('کد پیگیری پرداخت'),
        max_length=100,
        null=True,
        blank=True
    )
    settlement_tracking_code = models.CharField(
        _('کد پیگیری تسویه'),
        max_length=100,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'

    def __str__(self):
        return  f"پرداخت  {self.tracking_code}"

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = str(uuid.uuid4().hex)[:8]
        if not self.commission_rate:
            self.commission_rate = self.property.commission_rate
        if not self.commission_amount:
            self.calculate_amounts()
        super().save(*args, **kwargs)

    def calculate_amounts(self):
        """محاسبه کمیسیون و سهم مالک"""
        self.commission_amount = self.total_amount * self.commission_rate
        self.owner_amount = self.total_amount - self.commission_amount

    def mark_as_paid(self, payment_tracking_code):
        """ثبت پرداخت موفق"""
        self.payment_status = 'paid'
        self.payment_date = timezone.now()
        self.payment_tracking_code = payment_tracking_code
        self.save()

    def mark_as_settled(self, settlement_tracking_code):
        """ثبت تسویه موفق با مالک"""
        self.settlement_status = 'completed'
        self.settlement_date = timezone.now()
        self.settlement_tracking_code = settlement_tracking_code
        self.save()


class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ('payment', 'پرداخت'),
        ('refund', 'استرداد'),
        ('settlement', 'تسویه')
    ]


    TRANSACTION_STATUS = [
        ('pending', 'در انتظار'),
        ('success', 'موفق'),
        ('failed', 'ناموفق')
    ]
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        verbose_name=_('پرداخت')
    )
    
    amount = models.DecimalField(
        _('مبلغ'),
        max_digits=12,
        decimal_places=0
    )
    
    transaction_type = models.CharField(
        _('نوع تراکنش'),
        max_length=20,
        choices=TRANSACTION_TYPE
    )
    
    status = models.CharField(
        _('وضعیت'),
        max_length=20,
        choices=TRANSACTION_STATUS,
        default='pending'
    )
    
    tracking_code = models.CharField(
        _('کد پیگیری'),
        max_length=50,
        unique=True
    )
    
    bank_tracking_code = models.CharField(
        _('کد پیگیری بانک'),
        max_length=100,
        null=True
    )
    
    bank_reference_id = models.CharField(
        _('شناسه مرجع بانک'),
        max_length=100,
        null=True
    )
    
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش‌ها'

    def __str__(self):
        return f"تراکنش {self.tracking_code} - {self.get_transaction_type_display()}"

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = f"TRX-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)
class Settlement(models.Model):
    SETTLEMENT_STATUS = [
        ('pending', 'در انتظار تسویه'),
        ('processing', 'در حال تسویه'),
        ('completed', 'تسویه شده'),
        ('failed', 'تسویه ناموفق')
    ]


    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        verbose_name=_('پرداخت')
    )
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_('مالک')
    )
    
    amount = models.DecimalField(
        _('مبلغ'),
        max_digits=12,
        decimal_places=0
    )
    
    status = models.CharField(
        _('وضعیت'),
        max_length=20,
        choices=SETTLEMENT_STATUS,
        default='pending'
    )
    
    tracking_code = models.CharField(
        _('کد پیگیری'),
        max_length=50,
        unique=True,
        null=True
    )
    
    bank_tracking_code = models.CharField(
        _('کد پیگیری بانک'),
        max_length=100,
        null=True
    )
    
    bank_reference_id = models.CharField(
        _('شناسه مرجع بانک'),
        max_length=100,
        null=True
    )
    
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    settled_at = models.DateTimeField(_('تاریخ تسویه'), null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'تسویه حساب'
        verbose_name_plural = 'تسویه حساب‌ها'

    def __str__(self):
        return f"تسویه حساب  {self.tracking_code} - {self.owner.get_full_name()}"

    def generate_tracking_code(self):
        """تولید کد پیگیری تسویه"""
        return f"STL-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = self.generate_tracking_code()
        super().save(*args, **kwargs)

    def mark_as_completed(self, bank_tracking_code):
        """ثبت تسویه موفق"""
        self.status = 'completed'
        self.settled_at = timezone.now()
        self.bank_tracking_code = bank_tracking_code
        self.save()

    def process_settlement(self):
        """انجام عملیات تسویه"""
        if self.status != 'pending':
            return False
            
        self.status = 'processing'
        self.save()
        
        try:
            bank_service = BankService()
            result = bank_service.transfer_to_owner(
                amount=self.amount,
                destination=self.owner.bank_account,
                description=f"تسویه حساب - کد پیگیری: {self.tracking_code}"
            )
            
            if result['status'] == 'success':
                self.status = 'completed'
                self.bank_tracking_code = result['tracking_code']
                self.bank_reference_id = result['reference_id']
                self.settled_at = timezone.now()
                self.save()
                
                self.send_settlement_notification()
                return True
                
            self.status = 'failed'
            self.save()
            return False
            
        except Exception as e:
            self.status = 'failed'
            self.save()
            return False

    def send_settlement_notification(self):
        """ارسال نوتیفیکیشن تسویه به مالک"""
        notification_service = NotificationService()
        notification_service.send_settlement_notification(
            user=self.owner,
            amount=self.amount,
            tracking_code=self.tracking_code
        )

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def is_failed(self):
        return self.status == 'failed'
class Property(models.Model):
    title = models.CharField(_('عنوان'), max_length=200)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_properties',
        verbose_name=_('مالک')
    )
    commission_rate = models.DecimalField(
         _('نرخ کمیسیون'),
        max_digits=4,
        decimal_places=2,
        default=0.03,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    created_at = models.DateTimeField(
       _('تاریخ ایجاد'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('ملک')
        verbose_name_plural = _('املاک')

    def __str__(self):
        return self.title

    def commission_rate_display(self):
        """نمایش درصد کمیسیون"""
        return f'{self.commission_rate * 100}%'
    commission_rate_display.short_description = 'درصد کمیسیون'

class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
        ('refunded', 'مسترد شده')
    ]


    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refund_requests',
        verbose_name=_('پرداخت')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='refund_requests',
        verbose_name=_('کاربر')
    )
    amount = models.DecimalField(
        _('مبلغ درخواستی'),
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(1000)]
    )
    reason = models.TextField(_('دلیل استرداد'))
    status = models.CharField(
        _('وضعیت'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    bank_account = models.CharField(_('شماره شبا'), max_length=26)
    admin_note = models.TextField(_('توضیحات ادمین'), blank=True)
    created_at = models.DateTimeField(_('تاریخ ثبت'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('درخواست استرداد')
        verbose_name_plural = _('درخواست‌های استرداد')
        ordering = ['-created_at']

    def __str__(self):
        return f"درخواست استرداد {self.payment.tracking_code}"



