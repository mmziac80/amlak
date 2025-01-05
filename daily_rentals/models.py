# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class DailyRentProperty(models.Model):
    title = models.CharField(_('عنوان'), max_length=200)
    daily_price = models.DecimalField(_('قیمت روزانه'), max_digits=12, decimal_places=0)
    # ادامه فیلدها...

