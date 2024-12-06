
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from properties.models import DailyRentProperty, Booking
from .models import Payment, PaymentLog

User = get_user_model()

class PaymentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
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
            check_in='2024-01-01',
            check_out='2024-01-03',
            guests_count=2,
            total_price=2000000
        )
        
    def test_payment_init(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('payments:payment_init', args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Payment.objects.filter(booking=self.booking).exists()
        )

    def test_payment_callback_success(self):
        payment = Payment.objects.create(
            booking=self.booking,
            user=self.user,
            amount=2000000,
            status='pending'
        )
        response = self.client.get(
            reverse('payments:payment_callback'),
            {'Authority': payment.reference_id, 'Status': 'OK'}
        )
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'success')

    def test_payment_history(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('payments:payment_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/payment_history.html')
