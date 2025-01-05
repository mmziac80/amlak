# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.contrib.auth.models import UserManager
from django.db.models.signals import post_save
from django.dispatch import receiver

# Validators
phone_regex = RegexValidator(
    regex=r'^09\d{9}$',
    message="شماره موبایل باید در قالب 09123456789 باشد"
)

national_code_regex = RegexValidator(
    regex=r'^\d{10}$',
    message="کد ملی باید 10 رقم باشد"
)

class CustomUserManager(UserManager):
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('phone', '09000000000')
        extra_fields.setdefault('national_code', '0000000000')
        return self._create_user(username, email, password, **extra_fields)
class User(AbstractUser):
    objects = CustomUserManager()
    
    ROLES = [
        ('admin', 'مدیر'),
        ('agent', 'مشاور املاک'),
        ('owner', 'صاحب ملک'),
        ('user', 'کاربر عادی')
    ]

    # اطلاعات هویتی
    phone = models.CharField(
        _('شماره موبایل'),
        max_length=11,
        unique=True,
        validators=[phone_regex]
    )
    
    national_code = models.CharField(
        _('کد ملی'),
        max_length=10,
        unique=True,
        validators=[national_code_regex]
    )
    
    birth_date = models.DateField(
        _('تاریخ تولد'),
        null=True,
        blank=True
    )

    role = models.CharField(
        _('نوع کاربر'),
        max_length=10,
        choices=ROLES,
        default='user'
    )

    # تصاویر و مدارک
    avatar = models.ImageField(
        _('تصویر پروفایل'),
        upload_to='avatars/',
        null=True,
        blank=True
    )
    
    identity_document = models.FileField(
        _('مدارک هویتی'),
        upload_to='identity_docs/',
        blank=True,
        null=True
    )

    # تاییدیه‌ها
    is_phone_verified = models.BooleanField(_('تایید شده'), default=False)
    is_email_verified = models.BooleanField(_('ایمیل تایید شده'), default=False)
    identity_verified = models.BooleanField(_('هویت تایید شده'), default=False)

    # کد تایید
    otp = models.CharField(_('کد تایید موقت'), max_length=6, blank=True)
    otp_create_time = models.DateTimeField(_('تاریخ ایجاد کد'), null=True)
    email_verification_token = models.CharField(max_length=100, blank=True)

   # اطلاعات بانکی
    bank_account = models.CharField(
        _('شماره شبا'),
        max_length=26,
        blank=True,
        help_text=_('شماره شبا بدون حروف اضافه')
    )

    class Meta:
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')
        ordering = ['-date_joined']

    def __str__(self):
        return self.get_full_name() or self.username

    def get_full_name(self):
        """دریافت نام کامل کاربر"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    @property
    def age(self):
        """محاسبه سن کاربر"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year
        return None

    @property
    def is_complete(self):
        """بررسی تکمیل بودن پروفایل"""
        return all([
            self.first_name,
            self.last_name,
            self.phone,
            self.national_code,
            self.is_phone_verified
        ])

    def send_verification_code(self):
        """ارسال کد تایید به شماره موبایل کاربر"""
        from django.utils import timezone
        from datetime import timedelta
        import random

        code = str(random.randint(100000, 999999))
        self.otp = code
        self.otp_create_time = timezone.now() + timedelta(minutes=2)
        self.save()

        # TODO: ارسال کد به شماره موبایل
        return code

    def verify_code(self, code):
        """بررسی کد تایید"""
        from django.utils import timezone

        if not self.otp or not self.otp_create_time:
            return False

        if timezone.now() > self.otp_create_time:
            return False

        if code != self.otp:
            return False

        self.is_phone_verified = True
        self.otp = None
        self.otp_create_time = None
        self.save()
        return True

  
    def verify_identity(self):
        """تایید هویت کاربر"""
        if self.identity_document:
            self.identity_verified = True
            self.save()
            return True
        return False
    
    def get_active_properties(self):
        """دریافت املاک فعال کاربر"""
        return self.properties.filter(is_active=True)
    
    def get_total_payments(self):
        """مجموع کل پرداختی‌های کاربر"""
        return self.rent_payments.filter(payment_status='paid').aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0

    def get_total_earnings(self):
        """مجموع کل درآمدهای کاربر"""
        return self.received_payments.filter(payment_status='paid').aggregate(
            total=models.Sum('owner_amount')
        )['total'] or 0

    def get_pending_settlements(self):
        """دریافت تسویه‌حساب‌های در انتظار"""
        return self.settlements.filter(status='pending')
    
    def get_notifications(self):
        """دریافت اعلان‌های کاربر"""
        return self.notifications.filter(is_read=False)

    @property 
    def is_landlord(self):
        """بررسی اینکه آیا کاربر مالک ملک است"""
        return self.properties.exists()

    @property
    def profile_completion_percentage(self):
        """درصد تکمیل پروفایل"""
        fields = [
            self.first_name,
            self.last_name,
            self.phone,
            self.national_code,
            self.email,
            self.avatar,
            self.bank_account
        ]
        completed = len([f for f in fields if f])
        return int((completed / len(fields)) * 100)


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن')
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('کاربر')
    )
    
    gender = models.CharField(
        _('جنسیت'),
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    
    bio = models.TextField(
        _('درباره من'),
        blank=True
    )
    
    website = models.URLField(
        _('وبسایت'),
        blank=True
    )
    
    company = models.CharField(
       _('شرکت/آژانس'),
        max_length=100,
        blank=True
    )

    class Meta:
        verbose_name = _('پروفایل کاربر')
        verbose_name_plural = _('پروفایل‌های کاربر')

    def __str__(self):
        return f"پروفایل {self.user.get_full_name()}"

# Signals
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ایجاد پروفایل برای کاربر جدید"""
    if created and not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ذخیره پروفایل کاربری"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

class UserNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('payment', 'پرداخت'),
        ('booking', 'رزرو'),
        ('message', 'پیام'),
        ('system', 'سیستمی')
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('کاربر')
    )
    
    notification_type = models.CharField(
        _('نوع اعلان'),
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    
    title = models.CharField(
        _('عنوان'),
        max_length=200
    )
    
    message = models.TextField(_('متن پیام'))
    
    link = models.URLField(
        _('لینک'),
        blank=True
    )
    
    is_read = models.BooleanField(
        _('خوانده شده'),
        default=False
    )
    
    created_at = models.DateTimeField(
        _('تاریخ ایجاد'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('اعلان کاربر')
        verbose_name_plural = _('اعلان‌های کاربر')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title}"

    def mark_as_read(self):
        """علامت‌گذاری به عنوان خوانده شده"""
        self.is_read = True
        self.save()

   
class UserDevice(models.Model):
    DEVICE_TYPES = [
        ('web', 'مرورگر'),
        ('android', 'اندروید'), 
        ('ios', 'آیفون')
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name=_('کاربر')
    )
    
    device_type = models.CharField(
        _('نوع دستگاه'),
        max_length=10,
        choices=DEVICE_TYPES
    )
    
    device_id = models.CharField(
        _('شناسه دستگاه'),
        max_length=200,
        unique=True
    )
    
    push_token = models.CharField(
        _('توکن نوتیفیکیشن'),
        max_length=200,
        blank=True
    )
    
    last_login = models.DateTimeField(
        _('آخرین ورود'),
        auto_now=True
    )
    
    is_active = models.BooleanField(
        _('فعال'),
        default=True
    )

    class Meta:
        verbose_name = _('دستگاه کاربر')
        verbose_name_plural = _('دستگاه‌های کاربر')
        ordering = ['-last_login']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_device_type_display()}"

class UserActivity(models.Model):
    """ثبت فعالیت‌های کاربر"""
    
    ACTIVITY_TYPES = [
        ('login', 'ورود'),
        ('logout', 'خروج'),
        ('profile_update', 'بروزرسانی پروفایل'),
        ('password_change', 'تغییر رمز عبور'),
        ('verification', 'تایید شماره موبایل')
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
