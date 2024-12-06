from django.conf import settings

# تنظیمات درگاه زرین‌پال
ZARINPAL = {
    'MERCHANT_ID': 'YOUR-ZARINPAL-MERCHANT-ID',
    'SANDBOX': True,  # تنظیم True برای محیط تست
    'CALLBACK_URL': 'payments:payment_callback',
    'API': {
        'REQUEST': 'https://api.zarinpal.com/pg/v4/payment/request.json',
        'VERIFY': 'https://api.zarinpal.com/pg/v4/payment/verify.json',
        'STARTPAY': 'https://www.zarinpal.com/pg/StartPay/',
        'SANDBOX_REQUEST': 'https://sandbox.zarinpal.com/pg/v4/payment/request.json',
        'SANDBOX_VERIFY': 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json',
        'SANDBOX_STARTPAY': 'https://sandbox.zarinpal.com/pg/StartPay/'
    }
}

# تنظیمات درگاه آیدی پی
IDPAY = {
    'API_KEY': 'YOUR-IDPAY-API-KEY',
    'SANDBOX': True,
    'CALLBACK_URL': 'payments:payment_callback',
    'API': {
        'REQUEST': 'https://api.idpay.ir/v1.1/payment',
        'VERIFY': 'https://api.idpay.ir/v1.1/payment/verify',
        'SANDBOX_REQUEST': 'https://api.idpay.ir/v1.1/payment/test',
        'SANDBOX_VERIFY': 'https://api.idpay.ir/v1.1/payment/test/verify'
    }
}

# تنظیمات درگاه نکست‌پی
NEXTPAY = {
    'API_KEY': 'YOUR-NEXTPAY-API-KEY',
    'SANDBOX': True,
    'CALLBACK_URL': 'payments:payment_callback',
    'API': {
        'REQUEST': 'https://nextpay.org/nx/gateway/token',
        'VERIFY': 'https://nextpay.org/nx/gateway/verify',
        'SANDBOX_REQUEST': 'https://nextpay.org/nx/gateway/test/token',
        'SANDBOX_VERIFY': 'https://nextpay.org/nx/gateway/test/verify'
    }
}

# تنظیمات عمومی پرداخت
PAYMENT_SETTINGS = {
    'DEFAULT_GATEWAY': 'ZARINPAL',
    'CURRENCY': 'IRR',
    'DECIMAL_PLACES': 0,
    'MAX_DIGITS': 12,
    'EXPIRE_AFTER': 15,  # دقیقه
    'RETRY_TIMES': 3,
    'RETRY_INTERVAL': 1  # دقیقه
}

# پیکربندی لاگ پرداخت‌ها
PAYMENT_LOGGING = {
    'ENABLED': True,
    'LEVEL': 'INFO',
    'FORMAT': '%(asctime)s [%(levelname)s] %(message)s',
    'FILENAME': 'payments.log'
}

# تنظیمات API
API_SETTINGS = {
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1'],
    'VERSION_PARAM': 'version',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    'ORDERING_PARAM': 'order',
    'SEARCH_PARAM': 'search',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'payment': '50/day',
    },
    'EXCEPTION_HANDLER': 'payments.api.exception_handlers.custom_exception_handler'
}

# تنظیمات Swagger/OpenAPI
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEFAULT_MODEL_RENDERING': 'model',
    'DEFAULT_MODEL_DEPTH': 3,
}

# تنظیمات CORS
CORS_SETTINGS = {
    'CORS_ALLOW_ALL_ORIGINS': False,
    'CORS_ALLOWED_ORIGINS': [
        'https://mashhad-amlak.ir',
        'https://api.mashhad-amlak.ir',
    ] + getattr(settings, 'CORS_ALLOWED_ORIGINS', []),
    'CORS_ALLOW_METHODS': [
        'GET',
        'POST',
        'PUT',
        'PATCH',
        'DELETE',
        'OPTIONS'
    ],
    'CORS_ALLOW_HEADERS': [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    ],
    'CORS_EXPOSE_HEADERS': [
        'content-disposition',
    ],
    'CORS_PREFLIGHT_MAX_AGE': 86400,
}

# تنظیمات Cache
CACHE_SETTINGS = {
    'DEFAULT_TIMEOUT': 300,  # 5 دقیقه
    'PAYMENT_STATUS_TIMEOUT': 60,  # 1 دقیقه
    'REPORT_TIMEOUT': 3600,  # 1 ساعت
}

# تنظیمات Rate Limiting
RATE_LIMIT_SETTINGS = {
    'PAYMENT_INIT_RATE': '10/hour',
    'PAYMENT_VERIFY_RATE': '20/hour',
    'PAYMENT_REFUND_RATE': '5/day',
    'REPORT_RATE': '100/day',
}
