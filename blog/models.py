# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

User = get_user_model()

class Contact(models.Model):
    """فرم تماس با ما"""
    name = models.CharField(
        max_length=100,
        verbose_name=_('نام')
    )
    email = models.EmailField(
        verbose_name=_('ایمیل')
    )
    subject = models.CharField(
        max_length=200,
        verbose_name=_('موضوع')
    )
    message = models.TextField(
        verbose_name=_('پیام')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاریخ ایجاد')
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('خوانده شده')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('تماس')
        verbose_name_plural = _('تماس‌ها')

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Newsletter(models.Model):
    """فرم خبرنامه"""
    email = models.EmailField(
        unique=True,
        verbose_name=_('ایمیل')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('فعال')
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاریخ عضویت')
    )

    class Meta:
        verbose_name = _('خبرنامه')
        verbose_name_plural = _('خبرنامه‌ها')

    def __str__(self):
        return self.email


class FAQ(models.Model):
    """مدل سوالات متداول"""
    question = models.CharField(
        max_length=300,
        verbose_name=_('سوال')
    )
    answer = models.TextField(
        verbose_name=_('پاسخ')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('ترتیب')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('فعال')
    )

    class Meta:
        ordering = ['order']
        verbose_name = _('سوال متداول')
        verbose_name_plural = _('سوالات متداول')

    def __str__(self):
        return self.question


class Notification(models.Model):
    """مدل نوتیفیکیشن کاربر"""
    
    NOTIFICATION_TYPES = [
        ('info', 'اطلاع‌رسانی'),
        ('success', 'موفقیت'),
        ('warning', 'هشدار'),
        ('error', 'خطا')
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_notifications',
        verbose_name=_('کاربر')
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('عنوان')
    )
    
    message = models.TextField(
        verbose_name=_('پیام')
    )
    
    notification_type = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPES,
        default='info',
        verbose_name=_('نوع')
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('خوانده شده')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاریخ ایجاد')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('اعلان')
        verbose_name_plural = _('اعلانات')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"


class Feedback(models.Model):
    """مدل بازخورد کاربران"""
    
    RATING_CHOICES = [
        (1, '★'),
        (2, '★★'),
        (3, '★★★'),
        (4, '★★★★'),
        (5, '★★★★★')
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name=_('کاربر')
    )
    
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name=_('امتیاز')
    )
    
    comment = models.TextField(
        verbose_name=_('نظر')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاریخ ثبت')
    )
    
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('تایید شده')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('بازخورد')
        verbose_name_plural = _('بازخوردها')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rating}★"

class SiteSettings(models.Model):
    """مدل تنظیمات سایت"""
    
    site_name = models.CharField(
        max_length=100,
        verbose_name=_('نام سایت')
    )
    
    site_description = models.TextField(
        verbose_name=_('توضیحات سایت')
    )
    
    contact_email = models.EmailField(
        verbose_name=_('ایمیل تماس')
    )
    
    contact_phone = models.CharField(
        max_length=20,
        verbose_name=_('تلفن تماس')
    )
    
    address = models.TextField(
        verbose_name=_('آدرس')
    )
    
    instagram = models.URLField(
        blank=True,
        verbose_name=_('اینستاگرام')
    )
    
    telegram = models.URLField(
        blank=True,
        verbose_name=_('تلگرام')
    )
    
    whatsapp = models.URLField(
        blank=True,
        verbose_name=_('واتساپ')
    )
    
    about_us = models.TextField(
        verbose_name=_('درباره ما')
    )
    
    terms = models.TextField(
        verbose_name=_('شرایط و قوانین')
    )
    
    privacy = models.TextField(
        verbose_name=_('حریم خصوصی')
    )

    class Meta:
        verbose_name = _('تنظیمات سایت')
        verbose_name_plural = _('تنظیمات سایت')

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Post(models.Model):
    """مدل مدیریت وبلاگ"""
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('عنوان')
    )
    
    slug = models.SlugField(
        max_length=250,
        unique=True,
        verbose_name=_('اسلاگ')
    )
    
    content = models.TextField(
        verbose_name=_('محتوا')
    )
    
    image = models.ImageField(
        upload_to='blog/',
        blank=True,
        verbose_name=_('تصویر')
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('نویسنده')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاریخ ایجاد')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاریخ بروزرسانی')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('فعال')
    )

    class Meta:
        verbose_name = _('پست')
        verbose_name_plural = _('پست‌ها')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
