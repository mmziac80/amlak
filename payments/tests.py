from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from properties.models import DailyRentProperty, Booking
from .models import Payment, Transaction
from .constants import PAYMENT_STATUS
from .forms import PaymentFilterForm, PaymentRefundForm

User = get_user_model()

class PaymentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.property = DailyRentProperty.objects.create(
            title='Test Property',
            daily_price=1000000,
            max_guests=2
        )
        
        self.booking = Booking.objects.create(
            property=self.property,
            user=self.user,
            check_in='2024-01-01',
            check_out='2024-01-03',
            guests_count=2,
            total_price=2000000
        )

    def test_payment_creation(self):
        payment = Payment.objects.create(
            booking=self.booking,
            user=self.user,
            amount=2000000,
            status=PAYMENT_STATUS['PENDING']
        )
        self.assertEqual(payment.status, PAYMENT_STATUS['PENDING'])
        self.assertEqual(payment.amount, 2000000)
        self.assertIsNotNone(payment.expired_at)

    def test_payment_expiry(self):
        payment = Payment.objects.create(
            booking=self.booking,
            user=self.user,
            amount=2000000
        )
        self.assertTrue(payment.expired_at > timezone.now())

class PaymentViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.property = DailyRentProperty.objects.create(
            title='Test Property',
            daily_price=1000000,
            max_guests=2
        )
        
        self.booking = Booking.objects.create(
            property=self.property,
            user=self.user,
            check_in='2024-01-01',
            check_out='2024-01-03',
            guests_count=2,
            total_price=2000000
        )

    def test_payment_init_view(self):
        response = self.client.get(
            reverse('payments:payment_init', args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 200)
        
        payment = Payment.objects.filter(booking=self.booking).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, self.booking.total_price)

    def test_payment_history_view(self):
        Payment.objects.create(
            booking=self.booking,
            user=self.user,
            amount=2000000,
            status=PAYMENT_STATUS['SUCCESS']
        )
        
        response = self.client.get(reverse('payments:payment_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/history.html')
        self.assertContains(response, '2,000,000')

class PaymentFormTests(TestCase):
    def test_payment_filter_form(self):
        form_data = {
            'status': PAYMENT_STATUS['SUCCESS'],
            'date_from': '2024-01-01',
            'date_to': '2024-01-31'
        }
        form = PaymentFilterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_payment_refund_form(self):
        form_data = {
            'reason': 'Test refund reason',
            'bank_account': 'IR123456789012345678901234'
        }
        form = PaymentRefundForm(data=form_data)
        self.assertTrue(form.is_valid())

class TransactionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.property = DailyRentProperty.objects.create(
            title='Test Property',
            daily_price=1000000
        )
        self.booking = Booking.objects.create(
            property=self.property,
            user=self.user,
            total_price=2000000
        )
        self.payment = Payment.objects.create(
            booking=self.booking,
            user=self.user,
            amount=2000000
        )

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            payment=self.payment,
            amount=2000000,
            status=PAYMENT_STATUS['SUCCESS'],
            tracking_code='TEST123',
            bank_reference_id='REF123'
        )
        self.assertEqual(transaction.amount, 2000000)
        self.assertEqual(transaction.status, PAYMENT_STATUS['SUCCESS'])