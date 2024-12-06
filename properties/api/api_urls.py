
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'payments-api'

router = DefaultRouter()
router.register(r'payments', api_views.PaymentViewSet, basename='payment')
router.register(r'transactions', api_views.TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    
    # مسیر بررسی وضعیت پرداخت
    path(
        'status/<str:tracking_code>/',
        api_views.PaymentStatusView.as_view(),
        name='payment-status'
    ),
    
    # مسیر گزارش پرداخت‌ها
    path(
        'reports/',
        api_views.PaymentReportView.as_view(),
        name='payment-reports'
    ),
]
