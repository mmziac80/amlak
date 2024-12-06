
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .serializers import (
    PaymentSerializer,
    TransactionSerializer, 
    PaymentStatusSerializer,
    PaymentRefundSerializer,
    PaymentReportSerializer
)

payment_list_docs = swagger_auto_schema(
    operation_description="لیست پرداخت‌های کاربر را برمی‌گرداند",
    responses={
        200: PaymentSerializer(many=True),
        401: "احراز هویت نشده",
    }
)

payment_detail_docs = swagger_auto_schema(
    operation_description="جزئیات یک پرداخت را برمی‌گرداند",
    responses={
        200: PaymentSerializer(),
        401: "احراز هویت نشده",
        404: "پرداخت یافت نشد"
    }
)

payment_init_docs = swagger_auto_schema(
    operation_description="شروع فرآیند پرداخت",
    responses={
        200: openapi.Response(
            description="پرداخت با موفقیت شروع شد",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'payment_url': openapi.Schema(type=openapi.TYPE_STRING),
                    'authority': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: "خطا در شروع پرداخت",
        401: "احراز هویت نشده"
    }
)

payment_verify_docs = swagger_auto_schema(
    operation_description="تایید پرداخت",
    responses={
        200: openapi.Response(
            description="پرداخت با موفقیت تایید شد",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'ref_id': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: "خطا در تایید پرداخت",
        401: "احراز هویت نشده"
    }
)

payment_refund_docs = swagger_auto_schema(
    operation_description="درخواست استرداد وجه",
    request_body=PaymentRefundSerializer,
    responses={
        200: openapi.Response(
            description="درخواست استرداد ثبت شد",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: "خطا در ثبت درخواست استرداد",
        401: "احراز هویت نشده"
    }
)

payment_status_docs = swagger_auto_schema(
    operation_description="بررسی وضعیت پرداخت",
    responses={
        200: PaymentStatusSerializer(),
        401: "احراز هویت نشده",
        404: "پرداخت یافت نشد"
    }
)

payment_report_docs = swagger_auto_schema(
    operation_description="گزارش پرداخت‌ها",
    manual_parameters=[
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            description="تاریخ شروع (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            required=False
        ),
        openapi.Parameter(
            'end_date', 
            openapi.IN_QUERY,
            description="تاریخ پایان (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            required=False
        ),
    ],
    responses={
        200: PaymentReportSerializer(),
        401: "احراز هویت نشده"
    }
)

transaction_list_docs = swagger_auto_schema(
    operation_description="لیست تراکنش‌های کاربر را برمی‌گرداند",
    responses={
        200: TransactionSerializer(many=True),
        401: "احراز هویت نشده",
    }
)

transaction_detail_docs = swagger_auto_schema(
    operation_description="جزئیات یک تراکنش را برمی‌گرداند",
    responses={
        200: TransactionSerializer(),
        401: "احراز هویت نشده",
        404: "تراکنش یافت نشد"
    }
)
