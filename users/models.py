from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class User(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message="شماره موبایل باید در قالب 09123456789 باشد"
    )
    
    national_code_regex = RegexValidator(
        regex=r'^\d{10}$',
        message="کد ملی باید 10 رقم باشد"
    )

    phone = models.CharField(
        _('شماره موبایل'),
        max_length=11,
        unique=True,
        validators=[phone_regex],
        help_text=_('شماره موبایل خود را وارد کنید (مثال: 09123456789)')
    )
    
    national_code = models.CharField(
        _('کد ملی'),
        max_length=10,
        unique=True,
        validators=[national_code_regex],
        help_text=_('کد ملی 10 رقمی خود را وارد کنید')
    )
    
    is_verified = models.BooleanField(
        _('تایید شده'),
        default=False,
        help_text=_('نشان می‌دهد که آیا شماره موبایل کاربر تایید شده است')
    )
    
    verification_code = models.CharField(
        _('کد تایید'),
        max_length=6,
        blank=True,
        null=True
    )
    
    verification_code_expires = models.DateTimeField(
        _('تاریخ انقضای کد تایید'),
        blank=True,
        null=True
    )

    avatar = models.ImageField(
        _('تصویر پروفایل'),
        upload_to='avatars/',
        blank=True,
        null=True
    )

    birth_date = models.DateField(
        _('تاریخ تولد'),
        blank=True,
        null=True
    )

    address = models.TextField(
        _('آدرس'),
        blank=True
    )

    class Meta:
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')
        ordering = ['-date_joined']

    def __str__(self):
        return self.get_full_name() or self.username

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    @property
    def is_complete(self):
        """بررسی تکمیل بودن پروفایل کاربر"""
        return all([
            self.first_name,
            self.last_name,
            self.phone,
            self.national_code,
            self.is_verified
        ])

    def send_verification_code(self):
        """ارسال کد تایید به شماره موبایل کاربر"""
        from django.utils import timezone
        from datetime import timedelta
        import random

        # تولید کد تصادفی 6 رقمی
        code = str(random.randint(100000, 999999))
        
        # ذخیره کد و تاریخ انقضا
        self.verification_code = code
        self.verification_code_expires = timezone.now() + timedelta(minutes=2)
        self.save()

        # ارسال پیامک
        # TODO: اتصال به سرویس پیامک
        return code

    def verify_code(self, code):
        """تایید کد ارسال شده"""
        from django.utils import timezone

        if not self.verification_code or not self.verification_code_expires:
            return False

        if timezone.now() > self.verification_code_expires:
            return False

        if code != self.verification_code:
            return False

        self.is_verified = True
        self.verification_code = None
        self.verification_code_expires = None
        self.save()
        return True

class UserActivity(models.Model):
    """مدل ثبت فعالیت‌های کاربر"""
    
    ACTIVITY_TYPES = [
        ('login', 'ورود'),
        ('logout', 'خروج'),
        ('profile_update', 'بروزرسانی پروفایل'),
        ('password_change', 'تغییر رمز عبور'),
        ('verification', 'تایید شماره موبایل'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('کاربر')
    )
    
    activity_type = models.CharField(
        _('نوع فعالیت'),
        max_length=20,
        choices=ACTIVITY_TYPES
    )
    
    ip_address = models.GenericIPAddressField(
        _('آدرس IP'),
        null=True,
        blank=True
    )
    
    user_agent = models.CharField(
        _('مرورگر کاربر'),
        max_length=200,
        blank=True
    )
    
    created_at = models.DateTimeField(
        _('تاریخ ایجاد'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('فعالیت کاربر')
        verbose_name_plural = _('فعالیت‌های کاربر')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.get_activity_type_display()}"
