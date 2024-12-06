from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'
    verbose_name = 'مدیریت پرداخت‌ها'

    def ready(self):
        # ثبت سیگنال‌ها
        import payments.signals