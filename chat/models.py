# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class ChatRoom(models.Model):
    """اتاق چت"""
    ROOM_TYPES = [
        ('property', 'چت ملک'),
        ('support', 'پشتیبانی'),
        ('consultation', 'مشاوره'),
    ]
    
    type = models.CharField(_('نوع'), max_length=20, choices=ROOM_TYPES)
    users = models.ManyToManyField('users.User', related_name='chat_rooms')
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    is_active = models.BooleanField(_('فعال'), default=True)

    class Meta:
        verbose_name = _('اتاق چت')
        verbose_name_plural = _('اتاق‌های چت')

class Message(models.Model):
    """پیام"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(_('متن پیام'))
    attachment = models.FileField(_('فایل پیوست'), upload_to='chat/attachments/', null=True, blank=True)
    created_at = models.DateTimeField(_('تاریخ ارسال'), auto_now_add=True)
    is_read = models.BooleanField(_('خوانده شده'), default=False)

    class Meta:
        verbose_name = _('پیام')
        verbose_name_plural = _('پیام‌ها')
        ordering = ['created_at']
