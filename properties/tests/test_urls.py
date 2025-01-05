from django.test import TestCase
from django.urls import reverse, resolve
from properties.api.views import PropertyLocationViewSet

class TestPropertyUrls(TestCase):
    def test_location_url(self):
        url = reverse('property-locations-list')
        self.assertEqual(resolve(url).func.cls, PropertyLocationViewSet)
        
    def test_location_detail_url(self):
        url = reverse('property-locations-detail', args=[1])
        self.assertEqual(resolve(url).func.cls, PropertyLocationViewSet)
