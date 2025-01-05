# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from properties.models import DailyRentProperty, Booking
from .models import Payment, Transaction
from .constants import PAYMENT_STATUS
from .forms import PaymentFilterForm, RefundRequestForm

User = get_user_model()

class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            phone='09123456789',
            national_code='1234567890'
        )
        
        from django.utils import timezone
        current_time = timezone.now().time()

        self.daily_property = DailyRentProperty.objects.create(
            title='Test Daily Rental',
            description='Test property description',
            price=1000000,
            location='Test Location',
            address='Test Address, Street 123',
            area=80,
            rooms=2,
            status='available',
            owner=self.user,
            property_type='apartment',
            district='Test District',
            floor=2,
            total_floors=4,
            build_year=1400,
            document_type='official',
            direction='north',
            daily_price=1000000,
            check_in_time=current_time,
            check_out_time=current_time
        )      
        
        self.booking = Booking.objects.create(
            property=self.daily_property,
            user=self.user,
            check_in_date='2024-03-01',
            check_out_date='2024-03-03',
            guests_count=2,
            total_price=2000000
        )

        self.payment = Payment.objects.create(
            property=self.daily_property,
            renter=self.user,
            owner=self.daily_property.owner,
            total_amount=2000000,
            payment_status='pending',  # ??????? ?? payment_status
            check_in_date='2024-03-01',
            check_out_date='2024-03-03',
            commission_rate=Decimal('0.10') )  
    def test_payment_creation(self):
        self.assertEqual(self.payment.status, PAYMENT_STATUS['PENDING'])
        self.assertIsNotNone(self.payment.expired_at)

    def test_payment_expiry(self):
        self.assertTrue(self.payment.expired_at > timezone.now())

class PaymentViewTests(TestCase):
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
            'date_from': '2024-03-01',
            'date_to': '2024-03-31'
        }
        form = PaymentFilterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_payment_refund_form(self):
        form_data = {
            'reason': 'Test refund reason',
            'bank_account': 'IR123456789012345678901234'
        }
        form = RefundRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

class TransactionModelTests(TestCase):
    def setUp(self):
        # ????? ????? ???
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            phone='09123456789',
            national_code='1234567890'
        )
        
        # ????? ??? ????? ??????
        self.daily_property = DailyRentProperty.objects.create(
            title='Test Daily Rental',
            daily_price=1000000,
            owner=self.user
        )
        
        # ????? ????
        self.booking = Booking.objects.create(
            property=self.daily_property,
            user=self.user,
            check_in='2024-03-01',
            check_out='2024-03-03',
            total_price=2000000
        )
        
        # ????? ??????
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
