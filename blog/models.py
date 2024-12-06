from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Contact(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام')
    email = models.EmailField(verbose_name='ایمیل')
    subject = models.CharField(max_length=200, verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'تماس'
        verbose_name_plural = 'تماس‌ها'

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Newsletter(models.Model):
    email = models.EmailField(unique=True, verbose_name='ایمیل')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ عضویت')

    class Meta:
        verbose_name = 'خبرنامه'
        verbose_name_plural = 'خبرنامه‌ها'

    def __str__(self):
        return self.email

class FAQ(models.Model):
    question = models.CharField(max_length=300, verbose_name='سوال')
    answer = models.TextField(verbose_name='پاسخ')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        ordering = ['order']
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'

    def __str__(self):
        return self.question

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'اطلاع‌رسانی'),
        ('success', 'موفقیت'),
        ('warning', 'هشدار'),
        ('error', 'خطا')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='کاربر')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    message = models.TextField(verbose_name='پیام')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info', verbose_name='نوع')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلان‌ها'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"

class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks', verbose_name='کاربر')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name='امتیاز')
    comment = models.TextField(verbose_name='نظر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    is_approved = models.BooleanField(default=False, verbose_name='تایید شده')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'بازخورد'
        verbose_name_plural = 'بازخوردها'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rating}⭐"

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, verbose_name='نام سایت')
    site_description = models.TextField(verbose_name='توضیحات سایت')
    contact_email = models.EmailField(verbose_name='ایمیل تماس')
    contact_phone = models.CharField(max_length=20, verbose_name='تلفن تماس')
    address = models.TextField(verbose_name='آدرس')
    instagram = models.URLField(blank=True, verbose_name='اینستاگرام')
    telegram = models.URLField(blank=True, verbose_name='تلگرام')
    whatsapp = models.URLField(blank=True, verbose_name='واتساپ')
    about_us = models.TextField(verbose_name='درباره ما')
    terms = models.TextField(verbose_name='قوانین و مقررات')
    privacy = models.TextField(verbose_name='حریم خصوصی')

    class Meta:
        verbose_name = 'تنظیمات سایت'
        verbose_name_plural = 'تنظیمات سایت'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
