from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Sum, Count, Avg
from datetime import timedelta
import logging
from payments.services import BankService
from .models import Settlement
from django.db.models import Sum, Count, Avg, Max, Min




logger = logging.getLogger(__name__)

class SettlementService:
    def __init__(self):
        self.bank_service = BankService()
        self.notification_service = NotificationService()

    def process_settlement(self, settlement, processed_by=None):
        try:
            settlement.mark_as_processing(processed_by=processed_by)
            logger.info(f"Processing settlement {settlement.tracking_code}")
            
            # انتقال وجه به حساب مالک
            transfer_result = self.bank_service.transfer_to_owner(
                amount=settlement.amount,
                destination=settlement.bank_account,
                description=f"تسویه حساب {settlement.tracking_code}"
            )
            
            if transfer_result['status'] == 'success':
                settlement.mark_as_completed(
                    bank_reference_id=transfer_result['reference_id'],
                    processed_by=processed_by
                )
                self.notification_service.send_success_notification(settlement)
                logger.info(f"Settlement {settlement.tracking_code} completed successfully")
                return {'status': 'success', 'reference_id': transfer_result['reference_id']}
            
            settlement.mark_as_failed(
                reason=transfer_result['error'],
                processed_by=processed_by
            )
            self.notification_service.send_failure_notification(settlement)
            logger.error(f"Settlement {settlement.tracking_code} failed: {transfer_result['error']}")
            return {'status': 'failed', 'error': transfer_result['error']}
            
        except Exception as e:
            settlement.mark_as_failed(str(e), processed_by=processed_by)
            self.notification_service.send_failure_notification(settlement)
            logger.exception(f"Error processing settlement {settlement.tracking_code}")
            return {'status': 'failed', 'error': str(e)}

    def verify_settlement(self, settlement):
        if not settlement.bank_reference_id:
            return {'status': 'failed', 'error': 'شناسه تراکنش یافت نشد'}
            
        verify_result = self.bank_service.verify_transfer(settlement.bank_reference_id)
        logger.info(f"Verified settlement {settlement.tracking_code}: {verify_result['status']}")
        return verify_result

    def process_pending_settlements(self):
        pending_settlements = Settlement.objects.filter(
            status='pending',
            created_at__lte=timezone.now() - timedelta(hours=settings.SETTLEMENT_DELAY_HOURS)
        )
        
        results = {
            'processed': 0,
            'failed': 0,
            'total': pending_settlements.count()
        }
        
        for settlement in pending_settlements:
            result = self.process_settlement(settlement)
            if result['status'] == 'success':
                results['processed'] += 1
            else:
                results['failed'] += 1
                
        return results

    def cancel_stale_settlements(self):
        stale_settlements = Settlement.objects.filter(
            status='pending',
            created_at__lte=timezone.now() - timedelta(days=settings.SETTLEMENT_EXPIRY_DAYS)
        )
        
        cancelled_count = 0
        for settlement in stale_settlements:
            settlement.mark_as_cancelled(
                reason='درخواست به دلیل عدم پیگیری لغو شد',
            )
            self.notification_service.send_cancellation_notification(settlement)
            cancelled_count += 1
            
        return cancelled_count

class NotificationService:
    def send_success_notification(self, settlement):
        context = {
            'settlement': settlement,
            'site_logo': settings.SITE_LOGO,
            'support_phone': settings.SUPPORT_PHONE,
            'support_email': settings.SUPPORT_EMAIL,
            'dashboard_url': settings.DASHBOARD_URL
        }
        
        html_message = render_to_string('emails/settlement_success.html', context)
        
        try:
            send_mail(
                subject='تسویه حساب موفق',
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settlement.owner.email],
                html_message=html_message
            )
            logger.info(f"Success notification sent for settlement {settlement.tracking_code}")
        except Exception as e:
            logger.error(f"Failed to send success notification: {str(e)}")

    def send_failure_notification(self, settlement):
        context = {
            'settlement': settlement,
            'site_logo': settings.SITE_LOGO,
            'support_phone': settings.SUPPORT_PHONE,
            'support_email': settings.SUPPORT_EMAIL,
            'support_url': settings.SUPPORT_URL
        }
        
        html_message = render_to_string('emails/settlement_failed.html', context)
        
        try:
            send_mail(
                subject='خطا در تسویه حساب',
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settlement.owner.email],
                html_message=html_message
            )
            logger.info(f"Failure notification sent for settlement {settlement.tracking_code}")
        except Exception as e:
            logger.error(f"Failed to send failure notification: {str(e)}")

    def send_reminder_notification(self, settlements):
        for settlement in settlements:
            context = {
                'settlement': settlement,
                'site_logo': settings.SITE_LOGO,
                'support_phone': settings.SUPPORT_PHONE,
                'support_email': settings.SUPPORT_EMAIL,
                'settlements_url': settings.SETTLEMENTS_URL,
                'pending_count': settlements.count()
            }
            
            html_message = render_to_string('emails/settlement_reminder.html', context)
            
            try:
                send_mail(
                    subject='یادآوری تسویه حساب معوق',
                    message='',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settlement.owner.email],
                    html_message=html_message
                )
                logger.info(f"Reminder sent for settlement {settlement.tracking_code}")
            except Exception as e:
                logger.error(f"Failed to send reminder: {str(e)}")

    def send_cancellation_notification(self, settlement):
        context = {
            'settlement': settlement,
            'site_logo': settings.SITE_LOGO,
            'support_phone': settings.SUPPORT_PHONE,
            'support_email': settings.SUPPORT_EMAIL
        }
        
        html_message = render_to_string('emails/settlement_cancelled.html', context)
        
        try:
            send_mail(
                subject='لغو درخواست تسویه حساب',
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settlement.owner.email],
                html_message=html_message
            )
            logger.info(f"Cancellation notification sent for settlement {settlement.tracking_code}")
        except Exception as e:
            logger.error(f"Failed to send cancellation notification: {str(e)}")

class ReportService:
    def generate_monthly_report(self, month=None):
        if not month:
            month = timezone.now().replace(day=1)
            
        settlements = Settlement.objects.filter(
            created_at__year=month.year,
            created_at__month=month.month
        )
        
        successful_settlements = settlements.filter(status='completed')
        
        context = {
            'month_name': month.strftime('%B %Y'),
            'report_date': timezone.now(),
            'total_count': settlements.count(),
            'successful_count': successful_settlements.count(),
            'failed_count': settlements.filter(status='failed').count(),
            'pending_count': settlements.filter(status='pending').count(),
            'total_amount': successful_settlements.aggregate(Sum('amount'))['amount__sum'] or 0,
            'average_amount': successful_settlements.aggregate(Avg('amount'))['amount__avg'] or 0,
            'max_amount': successful_settlements.aggregate(Max('amount'))['amount__max'] or 0,
            'min_amount': successful_settlements.aggregate(Min('amount'))['amount__min'] or 0,
            'site_logo': settings.SITE_LOGO,
            'dashboard_url': settings.DASHBOARD_URL
        }
        
        html_message = render_to_string('emails/settlement_summary.html', context)
        
        try:
            send_mail(
                subject=f"گزارش تسویه حساب‌های {month.strftime('%B %Y')}",
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.REPORT_RECIPIENTS,
                html_message=html_message
            )
            logger.info(f"Monthly report sent for {month.strftime('%B %Y')}")
        except Exception as e:
            logger.error(f"Failed to send monthly report: {str(e)}")
