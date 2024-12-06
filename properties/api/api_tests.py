
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from properties.models import DailyRentProperty, Booking
from .models import Payment, Transaction
from .constants import PAYMENT_STATUS

User = get_user_model()

class PaymentAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
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
        
        self.payment = Payment.objects.create(
            booking=self.booking,
            user=self.user,
            amount=2000000,
            status=PAYMENT_STATUS['PENDING']
        )

    def test_payment_list(self):
        url = reverse('payments-api:payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_payment_detail(self):
        url = reverse('payments-api:payment-detail', args=[self.payment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], '2000000')

    def test_payment_init(self):
        url = reverse('payments-api:payment-init', args=[self.payment.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('payment_url', response.data)
        self.assertIn('authority', response.data)

    def test_payment_verify(self):
        url = reverse('payments-api:payment-verify', args=[self.payment.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_payment_refund(self):
        self.payment.status = PAYMENT_STATUS['SUCCESS']
        self.payment.save()
        
        url = reverse('payments-api:payment-refund', args=[self.payment.id])
        data = {
            'reason': 'Test refund reason',
            'bank_account': 'IR123456789012345678901234'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class TransactionAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.payment = Payment.objects.create(
            user=self.user,
            amount=2000000
        )
        
        self.transaction = Transaction.objects.create(
            payment=self.payment,
            amount=2000000,
            status=PAYMENT_STATUS['SUCCESS'],
            tracking_code='TEST123'
        )

    def test_transaction_list(self):
        url = reverse('payments-api:transaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_transaction_detail(self):
        url = reverse('payments-api:transaction-detail', args=[self.transaction.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tracking_code'], 'TEST123')

class PaymentStatusAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.payment = Payment.objects.create(
            user=self.user,
            amount=2000000,
            tracking_code='TEST123'
        )

    def test_payment_status(self):
        url = reverse('payments-api:payment-status', kwargs={'tracking_code': 'TEST123'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tracking_code'], 'TEST123')

class PaymentReportAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create some test payments
        Payment.objects.create(
            user=self.user,
            amount=1000000,
            status=PAYMENT_STATUS['SUCCESS']
        )
        Payment.objects.create(
            user=self.user,
            amount=2000000,
            status=PAYMENT_STATUS['SUCCESS']
        )
        Payment.objects.create(
            user=self.user,
            amount=3000000,
            status=PAYMENT_STATUS['FAILED']
        )

    def test_payment_report(self):
        url = reverse('payments-api:payment-reports')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_count'], 3)
        self.assertEqual(response.data['successful_count'], 2)
        self.assertEqual(response.data['failed_count'], 1)
        self.assertEqual(response.data['total_amount'], '3000000')
        self.assertEqual(response.data['success_rate'], 66.67)
