# -*- coding: utf-8 -*-

import time
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone
from .logging import SecurityLogger, PerformanceLogger, AuditLogger
from django.db import connection


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.audit_data = {
                'start_time': timezone.now(),
                'user_id': request.user.id,
                'path': request.path,
                'method': request.method,
                'ip': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            }

        response = self.get_response(request)

        if hasattr(request, 'audit_data'):
            duration = timezone.now() - request.audit_data['start_time']
            AuditLogger.log_user_action(
                request=request,
                action='page_view',
                object_id=None,
                details={
                    'path': request.audit_data['path'],
                    'method': request.audit_data['method'],
                    'duration': duration.total_seconds(),
                    'status_code': response.status_code,
                    'response_size': len(response.content) if hasattr(response, 'content') else 0
                }
            )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = (time.time() - start_time) * 1000

        if duration > settings.SLOW_QUERY_THRESHOLD:
            PerformanceLogger.log_api_response_time(
                request=request,
                response_time=duration,
                details={
                    'path': request.path,
                    'method': request.method,
                    'user_id': request.user.id if request.user.is_authenticated else None,
                    'query_count': len(connection.queries) if settings.DEBUG else None
                }
            )

        if hasattr(response, 'content') and len(response.content) > settings.MAX_RESPONSE_SIZE:
            PerformanceLogger.log_large_response(
                request=request,
                response_size=len(response.content)
            )

        return response

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # محدودیت دسترسی به پنل ادمین
        if request.path.startswith('/admin/'):
            if not self.check_admin_access(request):
                return HttpResponseForbidden('دسترسی غیرمجاز')

        # محدودیت تعداد درخواست
        if not self.check_rate_limit(request):
            return HttpResponseForbidden('تعداد درخواست‌های شما بیش از حد مجاز است')

        # بررسی تلاش‌های ناموفق ورود
        if request.path == settings.LOGIN_URL and request.method == 'POST':
            if not self.check_login_attempts(request):
                return HttpResponseForbidden('تعداد تلاش‌های ناموفق بیش از حد مجاز')

        response = self.get_response(request)

        # ثبت درخواست‌های مشکوک
        if response.status_code in [400, 401, 403, 404]:
            self.log_suspicious_request(request, response)

        return response

    def check_admin_access(self, request):
        if request.META.get('REMOTE_ADDR') not in settings.ADMIN_IP_WHITELIST:
            SecurityLogger.log_suspicious_activity(
                request,
                'unauthorized_admin_access',
                {'ip': request.META.get('REMOTE_ADDR')}
            )
            return False
        return True

    def check_rate_limit(self, request):
        key = f"rate_limit_{request.META.get('REMOTE_ADDR')}"
        requests = cache.get(key, 0)
        if requests >= settings.MAX_REQUESTS_PER_MINUTE:
            SecurityLogger.log_suspicious_activity(
                request,
                'rate_limit_exceeded',
                {'requests_count': requests}
            )
            return False
        cache.set(key, requests + 1, 60)  # 60 seconds expiry
        return True

    def check_login_attempts(self, request):
        key = f"login_attempts_{request.META.get('REMOTE_ADDR')}"
        attempts = cache.get(key, 0)
        if attempts >= settings.MAX_LOGIN_ATTEMPTS:
            SecurityLogger.log_suspicious_activity(
                request,
                'multiple_failed_logins',
                {'attempts': attempts}
            )
            return False
        cache.set(key, attempts + 1, settings.LOGIN_ATTEMPT_TIMEOUT)
        return True

    def log_suspicious_request(self, request, response):
        SecurityLogger.log_suspicious_activity(
            request,
            'suspicious_request',
            {
                'status_code': response.status_code,
                'path': request.path,
                'method': request.method,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referer': request.META.get('HTTP_REFERER', '')
            }
        )

class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.MAINTENANCE_MODE and not self.is_allowed_ip(request):
            return HttpResponseForbidden('سایت در حال بروزرسانی است')
        return self.get_response(request)

    def is_allowed_ip(self, request):
        return request.META.get('REMOTE_ADDR') in settings.MAINTENANCE_ALLOWED_IPS

