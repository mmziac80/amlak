# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'
    verbose_name = _('مدیریت پرداخت‌ها')


    def ready(self):
        # بارگذاری سیگنال‌ها
        import payments.signals


