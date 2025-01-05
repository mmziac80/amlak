# -*- coding: utf-8 -*-

import logging
import json
from django.conf import settings
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger('settlements')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

class SettlementLogger:
    @staticmethod
    def log_settlement_creation(settlement):
        logger.info(
            f"Settlement created - ID: {settlement.id}, "
            f"Amount: {settlement.amount}, "
            f"User: {settlement.owner.username}",
            extra={
                'settlement_id': settlement.id,
                'amount': str(settlement.amount),
                'user_id': settlement.owner.id,
                'tracking_code': settlement.tracking_code
            }
        )

    @staticmethod
    def log_settlement_status_change(settlement, old_status, new_status):
        logger.info(
            f"Settlement status changed - ID: {settlement.id}, "
            f"From: {old_status}, To: {new_status}, "
            f"User: {settlement.owner.username}",
            extra={
                'settlement_id': settlement.id,
                'old_status': old_status,
                'new_status': new_status,
                'user_id': settlement.owner.id
            }
        )

    @staticmethod
    def log_settlement_process(settlement, success, error=None):
        if success:
            logger.info(
                f"Settlement processed successfully - ID: {settlement.id}, "
                f"Reference: {settlement.bank_reference_id}",
                extra={
                    'settlement_id': settlement.id,
                    'reference_id': settlement.bank_reference_id,
                    'amount': str(settlement.amount)
                }
            )
        else:
            logger.error(
                f"Settlement process failed - ID: {settlement.id}, "
                f"Error: {error}",
                extra={
                    'settlement_id': settlement.id,
                    'error': str(error)
                }
            )

    @staticmethod
    def log_bank_transfer(settlement, response):
        logger.info(
            f"Bank transfer attempt - Settlement ID: {settlement.id}, "
            f"Amount: {settlement.amount}, "
            f"Response: {json.dumps(response, cls=DjangoJSONEncoder)}",
            extra={
                'settlement_id': settlement.id,
                'amount': str(settlement.amount),
                'response': response
            }
        )

class AuditLogger:
    @staticmethod
    def log_user_action(request, action, object_id, details=None):
        from .models import AuditLog
        
        AuditLog.objects.create(
            user=request.user,
            action=action,
            object_id=object_id,
            details=details,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            timestamp=timezone.now()
        )

    @staticmethod
    def log_settlement_view(request, settlement):
        AuditLogger.log_user_action(
            request=request,
            action='view_settlement',
            object_id=settlement.id,
            details={
                'tracking_code': settlement.tracking_code,
                'amount': str(settlement.amount)
            }
        )

    @staticmethod
    def log_settlement_process(request, settlement, success, error=None):
        AuditLogger.log_user_action(
            request=request,
            action='process_settlement',
            object_id=settlement.id,
            details={
                'success': success,
                'error': str(error) if error else None,
                'tracking_code': settlement.tracking_code
            }
        )

class SecurityLogger:
    @staticmethod
    def log_failed_login(request, username):
        logger.warning(
            f"Failed login attempt - Username: {username}",
            extra={
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'username': username
            }
        )

    @staticmethod
    def log_suspicious_activity(request, activity_type, details=None):
        logger.warning(
            f"Suspicious activity detected - Type: {activity_type}",
            extra={
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'user_id': request.user.id if request.user.is_authenticated else None,
                'activity_type': activity_type,
                'details': details
            }
        )

class PerformanceLogger:
    @staticmethod
    def log_slow_query(query_time, query_string):
        if query_time > settings.SLOW_QUERY_THRESHOLD:
            logger.warning(
                f"Slow query detected - Time: {query_time}ms",
                extra={
                    'query_time': query_time,
                    'query': query_string
                }
            )

    @staticmethod
    def log_api_response_time(request, response_time):
        logger.info(
            f"API response time - Path: {request.path}, Time: {response_time}ms",
            extra={
                'path': request.path,
                'method': request.method,
                'response_time': response_time
            }
        )

