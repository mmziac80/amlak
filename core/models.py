# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

"""
مدل‌های پایه استفاده شده مشترک در app های دیگر پروژه اجاره‌خونه
"""

class TimeStampedModel(models.Model):
    """
    مدل پایه برای ذخیره زمان ایجاد و بروزرسانی
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاریخ ایجاد')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاریخ بروزرسانی')
    )

    class Meta:
        abstract = True
