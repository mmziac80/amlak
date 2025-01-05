from decimal import Decimal
from pathlib import Path
from django.conf import settings  # این خط را در بالای فایل اضافه کنید

import os

# تنظیمات پایه conda و GDAL
CONDA_ROOT = r"C:\Users\Mohamadreza.AC\.conda\envs\newgis_env"
if os.name == 'nt':
    os.environ['OSGEO4W_ROOT'] = CONDA_ROOT
    os.environ['GDAL_DATA'] = str(Path(CONDA_ROOT) / "Library/share/gdal")
    os.environ['PROJ_LIB'] = str(Path(CONDA_ROOT) / "Library/share/proj")
    os.environ['PATH'] = str(Path(CONDA_ROOT) / "Library/bin") + ";" + os.environ['PATH']

    GDAL_LIBRARY_PATH = str(Path(CONDA_ROOT) / "Library/bin/gdal.dll")
    GEOS_LIBRARY_PATH = str(Path(CONDA_ROOT) / "Library/bin/geos_c.dll")

# تعریف کلیدها در سطح ماژول
NESHAN_API_KEY = 'web.ea06affc328a4934995818fed7a98b78'
NESHAN_SERVICE_KEY = 'service.c3d3d02a266e4672843003b4c50f1eb9'
# config/settings.py

GOOGLE_MAPS_API_KEY = 'AIzaSyDtbW6gijTK-YtYw7AHMo1LTdIuBhbxA0s'

# context processor برای دسترسی در تمپلیت‌ها


# تنظیمات پایه

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'your-secret-key'
DEBUG = True
ALLOWED_HOSTS = []

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]


# تنظیمات برنامه‌ها
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    'geopandas',
    'django_jalali',
    'django.contrib.gis', 
    'leaflet',
    'corsheaders',


    # Third-party apps
    'rest_framework',
    'channels',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    
    # Local apps
    'chat.apps.ChatConfig',
    'users.apps.UsersConfig',
    'properties.apps.PropertiesConfig',
    'payments.apps.PaymentsConfig',
    'settlements.apps.SettlementsConfig',
    'blog.apps.BlogConfig',
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'properties/templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'properties.context_processors.google_maps_api_key',  # اضافه کردن این خط

            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'amlak_db',
        'USER': 'postgres',
        'PASSWORD': '86963145',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}




# تنظیمات رمزنگاری
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# تنظیمات بین‌المللی‌سازی
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# تنظیمات فایل‌های استاتیک و رسانه
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# تنظیمات کاربر
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# تنظیمات کمیسیون
COMMISSION_SETTINGS = {
    'DEFAULT_RATE': Decimal('0.10'),
    'MIN_RATE': Decimal('0.05'),
    'MAX_RATE': Decimal('0.20'),
}

# تنظیمات پرداخت
PAYMENT_SETTINGS = {
    'MERCHANT_ID': 'your-merchant-id',
    'CALLBACK_URL': 'https://yourdomain.com/payments/callback/',
    'CURRENCY': 'IRR',
    'SANDBOX': DEBUG,
    'EXPIRE_IN': 15,
}

# تنظیمات SMS
if DEBUG:
    # تنظیمات محیط توسعه
    SMS_SETTINGS = {
        'IS_FAKE': True,
        'PROVIDER': 'FAKE',
        'API_KEY': 'fake-key',
        'SENDER': '3000****',
        'TEMPLATE_ID': 'test-template',
        'CALLBACK_URL': 'http://localhost:8000/sms/callback/',
        'DEBUG_CONSOLE': True  # نمایش پیام‌ها در کنسول
    }
else:
    # تنظیمات محیط تولید
    SMS_SETTINGS = {
        'IS_FAKE': False,
        'PROVIDER': 'KAVENEGAR',
        'API_KEY': 'your-real-api-key',
        'SENDER': 'your-real-number',
        'TEMPLATE_ID': 'your-template-id',
        'CALLBACK_URL': 'https://yourdomain.com/sms/callback/',
        'DEBUG_CONSOLE': False
    }

# تنظیمات ایمیل - تغییر برای محیط توسعه
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'your-email@gmail.com'
    EMAIL_HOST_PASSWORD = 'your-email-password'

DEFAULT_FROM_EMAIL = 'نام سایت <your-email@gmail.com>'

# تنظیمات REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # تغییر به AllowAny
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}






# تنظیمات Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# تنظیمات Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# تنظیمات لاگ
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'] if DEBUG else ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'payments': {
            'handlers': ['console', 'file'] if DEBUG else ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# تنظیمات کش
if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
            'TIMEOUT': 300
        }
    }

# تنظیمات Celery
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# تنظیمات امنیتی
SECURE_CONTENT_TYPE_NOSNIFF = True
CSP_DEFAULT_SRC = ("'self'", "'unsafe-eval'", "'unsafe-inline'", "*.googleapis.com")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-eval'", "'unsafe-inline'", "*.googleapis.com")
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# تنظیمات Content Security Policy
CSP_DEFAULT_SRC = (
    "'self'",
    "'unsafe-eval'",
    "'unsafe-inline'",
    "*.googleapis.com",
    "*.neshan.org",
)

CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-eval'",
    "'unsafe-inline'",
    "https://maps.googleapis.com",
    "https://cdn.jsdelivr.net",
    "https://static.neshan.org",
    "https://api.neshan.org",
)

CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://fonts.googleapis.com",
    "https://static.neshan.org",
)

CSP_IMG_SRC = (
    "'self'",
    "https:",
    "data:",
    "https://static.neshan.org",
)

CSP_CONNECT_SRC = (
    "'self'",
    "https://api.neshan.org",
)

