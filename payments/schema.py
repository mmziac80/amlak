
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
openapi.Info(
    title="API پرداخت املاک مشهد",
    default_version='v1',
    description="""
    API های سیستم پرداخت املاک مشهد

    قابلیت‌های اصلی:
    - مدیریت پرداخت‌ها
    - پیگیری تراکنش‌ها 
    - گزارش‌گیری
    - درخواست استرداد
    """,
    terms_of_service="https://www.mashhad-amlak.ir/terms/",
    contact=openapi.Contact(email="api@mashhad-amlak.ir"),
    license=openapi.License(name="MIT License"),
),
public=True,
permission_classes=[permissions.AllowAny],
)

# تنظیمات اضافی Schema
schema_view.schema.components.schemas.update({
'PaymentStatus': openapi.Schema(
    type=openapi.TYPE_STRING,
    enum=['pending', 'success', 'failed', 'expired', 'canceled', 'refunded'],
    description='وضعیت‌های ممکن پرداخت'
),
'PaymentType': openapi.Schema(
    type=openapi.TYPE_STRING,
    enum=['online', 'wallet', 'cash'],
    description='انواع روش پرداخت'
),
'Gateway': openapi.Schema(
    type=openapi.TYPE_STRING,
    enum=['zarinpal', 'idpay', 'nextpay'],
    description='درگاه‌های پرداخت'
),
})

# تگ‌های API
tags = [
openapi.Tag(
    name='payments',
    description='عملیات مربوط به پرداخت‌ها'
),
openapi.Tag(
    name='transactions',
    description='عملیات مربوط به تراکنش‌ها'
),
openapi.Tag(
    name='reports',
    description='گزارش‌های مالی و آماری'
),
]

# تنظیمات امنیتی
security_definitions = {
'Bearer': {
    'type': 'apiKey',
    'name': 'Authorization',
    'in': 'header',
    'description': 'توکن احراز هویت را با پیشوند Bearer وارد کنید'
}
}

# تنظیمات پاسخ‌های خطا
responses = {
400: openapi.Response(
    description='پارامترهای نامعتبر',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'error': openapi.Schema(type=openapi.TYPE_STRING)
        }
    )
),
401: openapi.Response(
    description='عدم احراز هویت',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'detail': openapi.Schema(type=openapi.TYPE_STRING)
        }
    )
),
403: openapi.Response(
    description='عدم دسترسی',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'detail': openapi.Schema(type=openapi.TYPE_STRING)
        }
    )
),
404: openapi.Response(
    description='یافت نشد',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'detail': openapi.Schema(type=openapi.TYPE_STRING)
        }
    )
),
500: openapi.Response(
    description='خطای سرور',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'error': openapi.Schema(type=openapi.TYPE_STRING)
        }
    )
)
}
