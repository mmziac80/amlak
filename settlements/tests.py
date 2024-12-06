from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from .models import Settlement
from .validators import PaymentAmountValidator, BankAccountValidator
from unittest.mock import patch
from .services import SettlementService, NotificationService
from .forms import SettlementCreateForm
from .forms import SettlementFilterForm
from django.urls import reverse
from .models import Settlement, AuditLog
from django.template import Template, Context




class SettlementModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            balance=1000000
        )

    def test_settlement_creation(self):
        settlement = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        self.assertTrue(settlement.tracking_code)
        self.assertEqual(settlement.status, 'pending')
        self.assertEqual(settlement.owner, self.user)
        self.assertEqual(settlement.amount, Decimal('100000'))

    def test_settlement_mark_as_completed(self):
        settlement = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        settlement.mark_as_completed('REF123')
        self.assertEqual(settlement.status, 'completed')
        self.assertEqual(settlement.bank_reference_id, 'REF123')
        self.assertIsNotNone(settlement.settled_at)

    def test_settlement_mark_as_failed(self):
        settlement = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        settlement.mark_as_failed('خطای تراکنش')
        self.assertEqual(settlement.status, 'failed')
        self.assertEqual(settlement.rejection_reason, 'خطای تراکنش')

    def test_settlement_mark_as_processing(self):
        settlement = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        settlement.mark_as_processing()
        self.assertEqual(settlement.status, 'processing')

    def test_get_bank_name_from_sheba(self):
        settlement = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR055000000000000000000000'
        )
        self.assertEqual(settlement.get_bank_name_from_sheba(), 'بانک اقتصاد نوین')

    def test_tracking_code_generation(self):
        settlement1 = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        settlement2 = Settlement.objects.create(
            owner=self.user,
            amount=200000,
            bank_account='IR123456789012345678901234'
        )
        self.assertNotEqual(settlement1.tracking_code, settlement2.tracking_code)
        self.assertTrue(settlement1.tracking_code.startswith('STL-'))
        self.assertTrue(settlement2.tracking_code.startswith('STL-'))

    def test_validators(self):
        # تست PaymentAmountValidator
        validator = PaymentAmountValidator()
        with self.assertRaises(ValidationError):
            validator(1000)  # کمتر از حداقل مبلغ
        with self.assertRaises(ValidationError):
            validator(2000000000)  # بیشتر از حداکثر مبلغ
        
        # تست BankAccountValidator
        validator = BankAccountValidator()
        with self.assertRaises(ValidationError):
            validator('123456')  # شماره شبای نامعتبر
        with self.assertRaises(ValidationError):
            validator('IR12345')  # شماره شبای کوتاه

class SettlementServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            balance=1000000
        )
        self.settlement = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        self.service = SettlementService()

    @patch('settlements.services.BankService.transfer_to_owner')
    def test_process_settlement_success(self, mock_transfer):
        mock_transfer.return_value = {
            'status': 'success',
            'reference_id': 'REF123'
        }
        
        result = self.service.process_settlement(self.settlement)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(self.settlement.status, 'completed')
        self.assertEqual(self.settlement.bank_reference_id, 'REF123')

    @patch('settlements.services.BankService.transfer_to_owner')
    def test_process_settlement_failure(self, mock_transfer):
        mock_transfer.return_value = {
            'status': 'failed',
            'error': 'خطای بانکی'
        }
        
        result = self.service.process_settlement(self.settlement)
        
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(self.settlement.status, 'failed')
        self.assertEqual(self.settlement.rejection_reason, 'خطای بانکی')

class NotificationServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.service = NotificationService()

    @patch('settlements.services.send_mail')
    def test_send_success_notification(self, mock_send_mail):
        settlement = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        
        self.service.send_settlement_notification(
            user=self.user,
            amount=100000,
            tracking_code=settlement.tracking_code
        )
        
        mock_send_mail.assert_called_once()

    @patch('settlements.services.SMSService.send')
    def test_send_sms_notification(self, mock_sms_send):
        mock_sms_send.return_value = True
        
        result = self.service.send_sms(
            phone='09123456789',
            message='تست پیامک'
        )
        
        self.assertTrue(result)
        mock_sms_send.assert_called_once()

from rest_framework.test import APITestCase
from rest_framework import status

class SettlementAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            balance=1000000
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_settlement(self):
        data = {
            'amount': 100000,
            'bank_account': 'IR123456789012345678901234'
        }
        response = self.client.post('/api/settlements/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Settlement.objects.count(), 1)
        self.assertEqual(Settlement.objects.get().amount, 100000)

    def test_list_settlements(self):
        Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        response = self.client.get('/api/settlements/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_process_settlement(self):
        settlement = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        admin_user = get_user_model().objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        self.client.force_authenticate(user=admin_user)
        
        response = self.client.post(f'/api/settlements/{settlement.tracking_code}/process/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        settlement.refresh_from_db()
        self.assertEqual(settlement.status, 'completed')

    def test_reject_settlement(self):
        settlement = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        admin_user = get_user_model().objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        self.client.force_authenticate(user=admin_user)
        
        data = {'reason': 'اطلاعات نادرست'}
        response = self.client.post(f'/api/settlements/{settlement.tracking_code}/reject/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        settlement.refresh_from_db()
        self.assertEqual(settlement.status, 'rejected')
        self.assertEqual(settlement.rejection_reason, 'اطلاعات نادرست')

    def test_filter_settlements(self):
        Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        Settlement.objects.create(
            owner=self.user,
            amount=200000,
            bank_account='IR123456789012345678901234',
            status='completed'
        )
        
        response = self.client.get('/api/settlements/?status=completed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.get('/api/settlements/?min_amount=150000')
        self.assertEqual(len(response.data), 1)

class SettlementFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            balance=1000000
        )

    def test_settlement_create_form_valid(self):
        form_data = {
            'amount': 100000,
            'bank_account': 'IR123456789012345678901234',
            'confirm_terms': True
        }
        form = SettlementCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_settlement_create_form_invalid_amount(self):
        form_data = {
            'amount': 1000,  # کمتر از حداقل مجاز
            'bank_account': 'IR123456789012345678901234',
            'confirm_terms': True
        }
        form = SettlementCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_settlement_create_form_invalid_bank_account(self):
        form_data = {
            'amount': 100000,
            'bank_account': '123456',  # شماره شبای نامعتبر
            'confirm_terms': True
        }
        form = SettlementCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('bank_account', form.errors)

    def test_settlement_filter_form_valid(self):
        form_data = {
            'date_from': '2024-01-01',
            'date_to': '2024-01-31',
            'status': 'completed',
            'min_amount': 50000,
            'max_amount': 1000000
        }
        form = SettlementFilterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_settlement_filter_form_invalid_dates(self):
        form_data = {
            'date_from': '2024-01-31',
            'date_to': '2024-01-01'  # تاریخ شروع بعد از تاریخ پایان
        }
        form = SettlementFilterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_settlement_filter_form_invalid_amounts(self):
        form_data = {
            'min_amount': 100000,
            'max_amount': 50000  # حداقل بیشتر از حداکثر
        }
        form = SettlementFilterForm(data=form_data)
        self.assertFalse(form.is_valid())

class SettlementViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            balance=1000000
        )
        self.client.login(username='testuser', password='testpass123')

    def test_settlement_list_view(self):
        Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        response = self.client.get(reverse('settlements:settlement-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settlements/settlement_list.html')
        self.assertEqual(len(response.context['settlements']), 1)

    def test_settlement_detail_view(self):
        settlement = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        response = self.client.get(
            reverse('settlements:settlement-detail', 
            kwargs={'tracking_code': settlement.tracking_code})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settlements/settlement_detail.html')
        self.assertEqual(response.context['settlement'], settlement)

    def test_settlement_create_view(self):
        response = self.client.get(reverse('settlements:settlement-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settlements/settlement_create.html')

        data = {
            'amount': 100000,
            'bank_account': 'IR123456789012345678901234',
            'confirm_terms': True
        }
        response = self.client.post(reverse('settlements:settlement-create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Settlement.objects.count(), 1)

    def test_settlement_dashboard_view(self):
        # ایجاد چند تسویه برای تست آمار
        Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        Settlement.objects.create(
            owner=self.user,
            amount=200000,
            bank_account='IR123456789012345678901234',
            status='completed'
        )

        response = self.client.get(reverse('settlements:settlement-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settlements/settlement_dashboard.html')
        self.assertIn('total_amount', response.context)
        self.assertIn('pending_count', response.context)
        self.assertIn('completed_count', response.context)

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(reverse('settlements:settlement-list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next={reverse("settlements:settlement-list")}')

class SettlementMiddlewareTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            balance=1000000
        )
        self.client.login(username='testuser', password='testpass123')

    def test_settlement_rate_limit_middleware(self):
        # تست محدودیت تعداد درخواست
        for _ in range(5):
            response = self.client.post(reverse('settlements:settlement-create'), {
                'amount': 100000,
                'bank_account': 'IR123456789012345678901234',
                'confirm_terms': True
            })
        
        response = self.client.post(reverse('settlements:settlement-create'), {
            'amount': 100000,
            'bank_account': 'IR123456789012345678901234',
            'confirm_terms': True
        })
        self.assertEqual(response.status_code, 429)

    def test_settlement_ip_whitelist_middleware(self):
        # تست IP های مجاز برای پنل مدیریت
        admin_user = get_user_model().objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        self.client.login(username='admin', password='admin123')
        
        with self.settings(ADMIN_IP_WHITELIST=['127.0.0.1']):
            response = self.client.get(reverse('settlements:settlement-dashboard'))
            self.assertEqual(response.status_code, 200)

        with self.settings(ADMIN_IP_WHITELIST=['1.1.1.1']):
            response = self.client.get(reverse('settlements:settlement-dashboard'))
            self.assertEqual(response.status_code, 403)

    def test_settlement_audit_log_middleware(self):
        # تست ثبت لاگ تغییرات
        settlement = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )
        
        response = self.client.post(
            reverse('settlements:settlement-process', kwargs={'tracking_code': settlement.tracking_code})
        )
        
        self.assertTrue(AuditLog.objects.filter(
            action='process_settlement',
            user=self.user,
            object_id=settlement.id
        ).exists())

class SettlementTemplateTagsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.settlement = Settlement.objects.create(
            owner=self.user,
            amount=100000,
            bank_account='IR123456789012345678901234'
        )

    def test_status_color_tag(self):
        template = Template('{% load settlement_tags %}{{ status|status_color }}')
        context = Context({'status': 'pending'})
        self.assertEqual(template.render(context), 'warning')

        context = Context({'status': 'completed'})
        self.assertEqual(template.render(context), 'success')

        context = Context({'status': 'failed'})
        self.assertEqual(template.render(context), 'danger')

    def test_format_bank_account_tag(self):
        template = Template('{% load settlement_tags %}{{ bank_account|format_bank_account }}')
        context = Context({'bank_account': 'IR123456789012345678901234'})
        self.assertEqual(template.render(context), 'IR 1234 5678 9012 3456 7890 1234')

    def test_settlement_status_badge_tag(self):
        template = Template('{% load settlement_tags %}{% settlement_status_badge settlement %}')
        context = Context({'settlement': self.settlement})
        rendered = template.render(context)
        self.assertIn('badge', rendered)
        self.assertIn('در انتظار بررسی', rendered)

    def test_remaining_time_tag(self):
        template = Template('{% load settlement_tags %}{{ settlement|remaining_time }}')
        self.settlement.created_at = timezone.now() - timezone.timedelta(hours=12)
        context = Context({'settlement': self.settlement})
        self.assertIn('12 ساعت', template.render(context))
