from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from ..models import Property, SaleProperty, RentProperty, DailyRentProperty
from decimal import Decimal, ROUND_DOWN

class TestPropertyLocationAPI(TestCase):
    def _create_test_property(self, title, lat=35.6892, lng=51.389, deal_type='sale'):
        """متد کمکی برای ساخت املاک تست"""
        from decimal import Decimal, ROUND_DOWN
        
        # تبدیل اعداد به Decimal با 6 رقم اعشار
        lat_decimal = Decimal(str(lat)).quantize(Decimal('0.000001'), rounding=ROUND_DOWN)
        lng_decimal = Decimal(str(lng)).quantize(Decimal('0.000001'), rounding=ROUND_DOWN)
        
        # داده‌های پایه مشترک بین همه انواع املاک
        base_data = {
            'title': title,
            'description': "توضیحات تست",
            'deal_type': deal_type,
            'status': 'available',
            'area': 100,
            'rooms': 2,
            'latitude': lat_decimal,
            'longitude': lng_decimal,
            'address': "آدرس تست",
            'owner': self.user,
            'is_active': True,
            'property_type': 'apartment',
            'district': 'منطقه تست',
            'floor': 2,
            'total_floors': 5,
            'build_year': 1400
        }


        # در بخش ایجاد املاک
        if deal_type == 'sale':
            property_data = {**base_data,
                            'document_type': 'سند شش دانگ',
                            'direction': 'شمالی'}
            property = SaleProperty(**property_data)
            property.total_price = Decimal('1000000')
            property.price_per_meter = Decimal('10000')

        elif deal_type == 'rent':
            property = RentProperty(**base_data)
            property.deposit = Decimal('100000000')
            property.monthly_rent = Decimal('5000000')

        else:  # daily
            from django.utils import timezone
            property = DailyRentProperty(**base_data)
            property.daily_price = Decimal('500000')
            property.check_in_time = timezone.now().time()
            property.check_out_time = timezone.now().time()
            property.max_guests = 2





    def setUp(self):
        self.base_url = '/api/properties/locations/'
        self.client = APIClient()
        
        # ایجاد کاربر تست
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # ایجاد املاک تست
        self.properties = [
            self._create_test_property("ملک فروشی", deal_type='sale'),
            self._create_test_property("ملک اجاره‌ای", deal_type='rent'),
            self._create_test_property("ملک روزانه", deal_type='daily')
        ]

            
    def test_location_data_structure(self):
        """تست ساختار داده‌های موقعیت"""
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(len(data['results']) > 0, "لیست املاک نباید خالی باشد")
        
        location = data['results'][0]
        required_fields = [
            'id', 'title', 'latitude', 'longitude',
            'address', 'deal_type', 'price_display', 'status'
        ]
        
        for field in required_fields:
            self.assertIn(field, location)

    def test_get_locations(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)

    def test_location_filtering(self):
        response = self.client.get(f'{self.base_url}?deal_type=sale')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(len(data['results']) > 0)
        for item in data['results']:
            self.assertEqual(item['deal_type'], 'sale')

    def test_coordinates_validation(self):
        """تست اعتبارسنجی محدوده مختصات"""
        test_cases = [
            {'latitude': 91, 'longitude': 51},
            {'latitude': 35, 'longitude': 181},
            {'latitude': -91, 'longitude': 51},
            {'latitude': 35, 'longitude': -181}
        ]

        print("\n=== تست اعتبارسنجی مختصات ===")
        for coords in test_cases:
            print(f"\nتست مختصات: lat={coords['latitude']}, lng={coords['longitude']}")
            try:
                property = self._create_test_property(
                    title="تست محدوده",
                    lat=coords['latitude'],
                    lng=coords['longitude']
                )
                print("خطا: ValidationError رخ نداد!")
            except ValidationError as e:
                print(f"OK: خطای اعتبارسنجی: {e}")

    def test_api_response_format(self):
        """تست ساختار پاسخ API"""
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # بررسی وجود کلیدهای اصلی
        self.assertIn('results', data)
        self.assertIn('count', data)
        
        # بررسی نوع داده‌ها
        results = data['results']
        self.assertIsInstance(results, list)
        
        if len(results) > 0:
            first_item = results[0]
            self.assertIsInstance(first_item, dict)
            self.assertIsInstance(first_item['id'], int)
            self.assertIsInstance(first_item['title'], str)

    def test_nearby_properties(self):
        """تست جستجوی املاک نزدیک"""
        # پاک کردن املاک قبلی
        Property.objects.all().delete()
        
        # ایجاد املاک با فواصل مختلف
        test_locations = [
            ("ملک خیلی نزدیک", 35.705, 51.405),  # ~0.7 km
            ("ملک نزدیک", 35.71, 51.41),          # ~1.5 km
            ("ملک مرزی", 35.74, 51.44),           # ~4.8 km
            ("ملک دور", 35.8, 51.5)               # ~12 km
        ]
        
        # اضافه کردن print برای نمایش املاک ایجاد شده
        print("\n=== املاک ایجاد شده ===")
        for title, lat, lng in test_locations:
            prop = self._create_test_property(title, lat=lat, lng=lng)
            print(f"ملک: {title}")
            print(f"مختصات: ({lat}, {lng})")

        # تست API با مرکز و شعاع مشخص
        center_lat, center_lng = 35.7, 51.4
        
        # اضافه کردن print برای نمایش فواصل محاسبه شده
        print("\n=== فواصل محاسبه شده ===")
        for prop in Property.objects.all():
            distance = prop.calculate_distance(center_lat, center_lng)
            print(f"فاصله {prop.title} تا مرکز: {distance:.2f} کیلومتر")

        response = self.client.get(
            f'{self.base_url}nearby/',
            {
                'latitude': center_lat,
                'longitude': center_lng,
                'radius': 5  # کیلومتر
            }
        )
        
        # اضافه کردن print برای نمایش نتایج API
        print("\n=== نتایج API ===")
        data = response.json()
        print(f"تعداد نتایج: {len(data['results'])}")
        for item in data['results']:
            print(f"عنوان: {item['title']}")
            print(f"فاصله: {item.get('distance', 'نامشخص')} کیلومتر")
        
        # بررسی نتایج
        titles = [p['title'] for p in data['results']]
        expected_in = ["ملک خیلی نزدیک", "ملک نزدیک", "ملک مرزی"]
        expected_out = ["ملک دور"]
        
        # اضافه کردن print برای نمایش نتیجه بررسی
        print("\n=== نتیجه بررسی ===")
        for title in expected_in:
            result = title in titles
            print(f"{title}: {'پیدا شد' if result else 'پیدا نشد!'}")
        
        for title in expected_out:
            result = title not in titles
            print(f"{title}: {'خارج از محدوده' if result else 'در محدوده!'}")

    def test_price_display_format(self):
            """تست فرمت نمایش قیمت برای انواع مختلف املاک"""
            # ایجاد املاک تست با انواع مختلف قیمت‌گذاری
            properties = [
                self._create_test_property("ملک فروشی 1", deal_type='sale'),
                self._create_test_property("ملک اجاره‌ای 1", deal_type='rent'),
                self._create_test_property("ملک روزانه 1", deal_type='daily')
            ]
            
            # درخواست به API
            response = self.client.get(self.base_url)
            self.assertEqual(response.status_code, 200)
            data = response.json()['results']
            
            # بررسی فرمت قیمت برای هر نوع ملک
            for item in data:
                self.assertIn('price_display', item)
                if item['deal_type'] == 'sale':
                    self.assertIn('تومان', item['price_display'])
                elif item['deal_type'] == 'rent':
                    self.assertIn('ودیعه', item['price_display'])
                    self.assertIn('اجاره', item['price_display'])
                else:  # daily rent
                    self.assertIn('شبی', item['price_display'])