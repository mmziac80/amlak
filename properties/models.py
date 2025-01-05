# -*- coding: utf-8 -*-
# Python standard library imports
import json
from django.db import models
from django.db.models import QuerySet
from typing import TypedDict, Optional
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import Distance as D
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from typing import TYPE_CHECKING, Dict, List, Optional, Union, Any
from django.db.models import AutoField
from django.utils import timezone
from decimal import Decimal
from math import radians, sin, cos, sqrt, atan2
from datetime import date
import logging

# Django imports
from django.contrib.auth import get_user_model
# Third party imports
from jdatetime import datetime as jdatetime
from persiantools.jdatetime import JalaliDate
# Type checking imports
if TYPE_CHECKING:
    from .models import SaleProperty, RentProperty, DailyRentProperty

# Logger setup
logger = logging.getLogger(__name__)


User = get_user_model()

# تعریف دقیق ساختار location
class LocationDict(TypedDict):
    lat: float
    lng: float

class MapData(TypedDict):
    id: int
    title: str
    location: Optional[LocationDict]
    deal_type: str
    address: str
    price: str
    url: str

class Property(models.Model):
        # اضافه کردن type hint برای id
    id: AutoField
    # Booking relation
    bookings = models.ManyToManyField(
        'Booking',
        related_name='properties',
        blank=True
    )

    DEAL_TYPE_CHOICES = (
        ('sale', 'فروش'),
        ('rent', 'اجاره'),
        ('daily', 'اجاره روزانه')
    )
    
    PROPERTY_STATUS = [
        ('available', 'در دسترس'),
        ('sold', 'فروخته شده'),
        ('rented', 'اجاره داده شده'),
        ('reserved', 'رزرو شده'),
    ]
    PROPERTY_TYPES = [
        ('apartment', 'آپارتمان'),
        ('villa', 'ویلا'),
        ('office', 'دفتر کار'),
        ('store', 'مغازه'),
        ('land', 'زمین'),
    ]

    # Basic fields
    title = models.CharField(_('عنوان'), max_length=250, null=True, blank=True)
    description = models.TextField(_('توضیحات'), null=True, blank=True)
    deal_type = models.CharField(_('نوع معامله'), max_length=10, choices=DEAL_TYPE_CHOICES, default='rent', null=True, blank=True)
    status = models.CharField(_('وضعیت'), max_length=20, choices=PROPERTY_STATUS, null=True, blank=True)

    # Physical characteristics
    area = models.PositiveIntegerField(_('متراژ'), null=True, blank=True)
    rooms = models.PositiveSmallIntegerField(_('تعداد اتاق'), null=True, blank=True)

    # Location fields
    location = models.PointField(
        _('موقعیت مکانی'),
        geography=True,
        null=True,
        blank=True,
        spatial_index=True,
        srid=4326
    )
        # Relations
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='real_properties', verbose_name=_('مالک'), null=True, blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_properties', blank=True)
    features = models.ManyToManyField('PropertyFeature', verbose_name=_('امکانات'), blank=True)
   # اضافه کردن فیلدهای مهم
    floor = models.IntegerField(_('طبقه'), null=True, blank=True)
    total_floors = models.IntegerField(_('تعداد کل طبقات'), null=True, blank=True)
    build_year = models.PositiveIntegerField(_('سال ساخت'), null=True, blank=True)
    property_type = models.CharField(_('نوع ملک'), max_length=20, choices=PROPERTY_TYPES, null=True, blank=True)
    direction = models.CharField(_('جهت ساختمان'), max_length=50, null=True, blank=True)
    # Management fields 
    is_featured = models.BooleanField(_('ویژه'), default=False)
    is_active = models.BooleanField(_('فعال'), default=True)
    updated_at = models.DateTimeField(auto_now=True)
    distance = None
        # امکانات به صورت boolean
    storage = models.BooleanField(default=False)
    package = models.BooleanField(default=False)
    renovation = models.BooleanField(default=False)
    security = models.BooleanField(default=False)
    balcony = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
        # فیلدهای جدید را اضافه کنید
    parking = models.BooleanField(default=False, verbose_name="پارکینگ")
    elevator = models.BooleanField(default=False, verbose_name="آسانسور")
    district = models.CharField(max_length=100, verbose_name="منطقه", default="نامشخص")
    address = models.TextField(
        verbose_name="آدرس",
        null=True,
        blank=True,
        help_text="آدرس کامل ملک را وارد کنید",
        default="نامشخص"
    )
    views_count = models.PositiveIntegerField(
        default=0, 
        verbose_name="تعداد بازدید"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="تاریخ ایجاد"
    )
    
    def increment_views(self) -> None:
        """
        افزایش تعداد بازدید و ذخیره آن
        فقط فیلد views_count بروز می‌شود
        """
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def get_popularity_score(self) -> float:
        """
        محاسبه امتیاز محبوبیت بر اساس تعداد بازدید و سن آگهی
        
        Returns:
            float: امتیاز محبوبیت از 0 تا 100
        """
        age = (timezone.now() - self.created_at).days
        return (self.views_count / (age + 1)) * 100
    def get_features_display(self) -> list[str]:
        """
        نمایش لیست امکانات فعال ملک
        
        Returns:
            list[str]: لیست امکانات به فارسی
        """
        features = []
        if self.parking:
            features.append('پارکینگ')
        if self.elevator:
            features.append('آسانسور')
        return features

    def get_full_address(self) -> str:
        """
        ترکیب منطقه و آدرس کامل
        
        Returns:
            str: آدرس کامل با فرمت: منطقه - آدرس
        """
        parts = [self.district, self.address]
        return ' - '.join(filter(None, parts))


    @property
    def latitude(self) -> Optional[float]:
        """دریافت عرض جغرافیایی"""
        if self.location and isinstance(self.location, Point):
            return float(self.location.y)
        return None

    @property 
    def longitude(self) -> Optional[float]:
        """دریافت طول جغرافیایی"""
        if self.location:
            return float(self.location.x)
        return None

    def set_location(self, lat: float, lng: float) -> None:
        """تنظیم موقعیت جغرافیایی"""
        self.location = Point(lng, lat, srid=4326)

    def get_location_dict(self) -> Optional[LocationDict]:
        """دریافت موقعیت به صورت دیکشنری"""
        if self.location:
            return {
                'lat': float(self.location.y),
                'lng': float(self.location.x)
            }
        return None
    def save(self, *args, **kwargs):
        if isinstance(self.location, dict):
            try:
                self.location = Point(
                    float(self.location.get('lng', 0)),
                    float(self.location.get('lat', 0)),
                    srid=4326
                )
            except (TypeError, ValueError):
                pass
        super().save(*args, **kwargs)


    def clean(self):
        super().clean()
        if self.location:
            lat = self.location.y
            lng = self.location.x
            
            if not (-90 <= lat <= 90):
                raise ValidationError({
                    'location': [f'عرض جغرافیایی {lat} خارج از محدوده مجاز است']  # پیام در لیست
                })
            
            if not (-180 <= lng <= 180):
                raise ValidationError({
                    'location': [f'طول جغرافیایی {lng} خارج از محدوده مجاز است']  # پیام در لیست
                })

    def get_price_display(self):
        self.saleproperty: 'SaleProperty'
        self.rentproperty: 'RentProperty'
        self.dailyrentproperty: 'DailyRentProperty'

        if hasattr(self, 'saleproperty'):
            return f"قیمت: {self.saleproperty.total_price:,} تومان"
        elif hasattr(self, 'rentproperty'):
            return f"ودیعه: {self.rentproperty.deposit:,} - اجاره: {self.rentproperty.monthly_rent:,}"
        elif hasattr(self, 'dailyrentproperty'):
            return f"اجاره روزانه: {self.dailyrentproperty.daily_price:,}"
        return "قیمت تعیین نشده"

    def get_property_type(self):
        if hasattr(self, 'saleproperty'):
            return self.saleproperty.property_type
        elif hasattr(self, 'rentproperty'):
            return self.rentproperty.property_type
        elif hasattr(self, 'dailyrentproperty'):
            return self.dailyrentproperty.property_type
        return None

    def to_map_data(self) -> MapData:
        location = self.get_location_dict()
        return {
            'id': self.id,
            'title': self.title or '',
            'location': location,
            'deal_type': self.deal_type or '',
            'address': self.address or '',
            'price': self.get_price_display(),
            'url': self.get_absolute_url()
        }

    def get_absolute_url(self) -> str:
        if hasattr(self, 'saleproperty'):
            return reverse('properties:sale_detail', args=[self.id])
        elif hasattr(self, 'rentproperty'):
            return reverse('properties:rent_detail', args=[self.id])
        elif hasattr(self, 'dailyrentproperty'):
            return reverse('properties:daily_detail', args=[self.id])
        return '#'

    def calculate_distance(self, lat2: float, lon2: float) -> float:
        """
        محاسبه فاصله بین دو نقطه با GeoDjango
        
        Args:
            lat2: عرض جغرافیایی مقصد
            lon2: طول جغرافیایی مقصد
            
        Returns:
            float: فاصله به کیلومتر
        """
        if not self.location:
            return float('inf')
            
        try:
            target = Point(lon2, lat2, srid=4326)
            distance = D(m=self.location.distance(target))
            return float(distance.km)
            
        except (ValueError, TypeError) as e:
            logger.error(f"خطا در محاسبه فاصله: {e}")
            return float('inf')




    def check_availability(self, check_in: date, check_out: date) -> bool:
        """
        بررسی در دسترس بودن ملک در بازه زمانی مشخص
        
        Args:
            check_in: تاریخ ورود
            check_out: تاریخ خروج
            
        Returns:
            bool: True اگر در دسترس باشد، False در غیر این صورت
        """
        try:
            if check_in > check_out:
                logger.warning(f"تاریخ ورود {check_in} بعد از تاریخ خروج {check_out} است")
                return False

            conflicting_bookings = self.bookings.filter(
                Q(check_in_date__lte=check_out) & 
                Q(check_out_date__gte=check_in),
                status='confirmed'
            )
            
            is_available = not conflicting_bookings.exists()
            logger.info(f"وضعیت دسترسی برای {check_in} تا {check_out}: {is_available}")
            
            return is_available

        except Exception as e:
            logger.error(f"خطا در بررسی دسترسی: {e}")
            return False
    @classmethod
    def get_properties_within_radius(
        cls, 
        lat: float, 
        lng: float, 
        radius_km: float = 5
    ) -> models.QuerySet:
        try:
            user_location = Point(lng, lat, srid=4326)
            return cls.objects.filter(
                location__isnull=False,
                is_active=True
            ).annotate(
                distance=Distance('location', user_location)
            ).filter(
                distance__lte=D(km=radius_km)
            ).select_related(
                'saleproperty',
                'rentproperty',
                'dailyrentproperty'
            ).order_by('distance')
        except (ValueError, TypeError):
            return cls.objects.none()
    def __str__(self):
        return self.title or ''

    class Meta:
        verbose_name = _('ملک')
        verbose_name_plural = _('املاک')
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        indexes = [
            models.Index(fields=['-created_at']),
        ]



class SaleProperty(Property):
    # فیلدهای مختص فروش
    document_type = models.CharField(_('نوع سند'), max_length=100)
    total_price = models.DecimalField(_('قیمت کل'), max_digits=12, decimal_places=0)
    price_per_meter = models.DecimalField(_('قیمت هر متر'), max_digits=12, decimal_places=0)
    is_exchangeable = models.BooleanField(_('قابل معاوضه'), default=False)
    exchange_description = models.TextField(_('توضیحات معاوضه'), blank=True)
    is_negotiable = models.BooleanField(_('قابل مذاکره'), default=False)

    class Meta:
        verbose_name = _('ملک فروشی')
        verbose_name_plural = _('املاک فروشی')
    
    def save(self, *args, **kwargs):
        self.deal_type = 'sale'
        super().save(*args, **kwargs)

class RentProperty(Property):
    
    # شرایط اجاره
    monthly_rent = models.DecimalField(_('اجاره ماهیانه'), max_digits=12, decimal_places=0)
    deposit = models.DecimalField(_('ودیعه'), max_digits=12, decimal_places=0)
    is_convertible = models.BooleanField(_('قابل تبدیل'), default=False)
    minimum_lease = models.IntegerField(_('حداقل مدت اجاره'), default=12)
    has_transfer_fee = models.BooleanField(_('کمیسیون دارد'), default=True)

    def save(self, *args, **kwargs):
        self.deal_type = 'rent'  # تنظیم خودکار نوع معامله
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('ملک اجاره‌ای')
        verbose_name_plural = _('املاک اجاره‌ای')
       
class DailyRentProperty(Property):

    # شرایط اقامت
    daily_price = models.DecimalField(_('قیمت روزانه'), max_digits=12, decimal_places=0)
    min_stay = models.PositiveIntegerField(
        _('حداقل مدت اقامت'),
        default=1,
        validators=[MinValueValidator(1)],
        help_text=_('حداقل تعداد شب‌های اقامت')
    )
    maximum_days = models.IntegerField(_('حداکثر مدت اقامت'), null=True, blank=True)
    max_guests = models.PositiveIntegerField(_('حداکثر تعداد مهمان'), default=2)
    extra_person_fee = models.DecimalField(_('هزینه نفر اضافه'), max_digits=10, decimal_places=0, null=True, blank=True)
    check_in_time = models.TimeField(_('ساعت ورود'))
    check_out_time = models.TimeField(_('ساعت خروج'))
    def calculate_price(self, check_in_date, check_out_date) -> int:
        """محاسبه قیمت کل اقامت"""
        # محاسبه تعداد روزها
        days = (check_out_date - check_in_date).days
        
        # اعتبارسنجی تعداد روزها
        if days < self.min_stay:
            raise ValidationError(f'حداقل مدت اقامت {self.min_stay} شب است')
        
        if self.maximum_days and days > self.maximum_days:
            raise ValidationError(f'حداکثر مدت اقامت {self.maximum_days} شب است')
        
        # محاسبه قیمت پایه
        total_price = self.daily_price * days
        
        return int(total_price)


    def save(self, *args, **kwargs):
        self.deal_type = 'daily'  # تنظیم خودکار نوع معامله
        super().save(*args, **kwargs)

    bookings: models.Manager['Booking']
    def is_available(self, check_in, check_out) -> bool:
            """
            بررسی در دسترس بودن ملک در بازه زمانی مشخص شده
            """
            return not self.bookings.filter(
                Q(check_in_date__lte=check_out) &
                Q(check_out_date__gte=check_in),
                status='confirmed'
            ).exists()



    class Meta:
        verbose_name = _('ملک اجاره روزانه')
        verbose_name_plural = _('املاک اجاره روزانه')




class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_('تصویر'), upload_to='properties/')
    title = models.CharField(_('عنوان'), max_length=100, blank=True)  # اضافه شد
    order = models.PositiveIntegerField(_('ترتیب'), default=0)  # اضافه شد
    is_main = models.BooleanField(_('تصویر اصلی'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('تصویر ملک')
        verbose_name_plural = _('تصاویر ملک')
        ordering = ['order', '-created_at']  # ترتیب بر اساس order


class PropertyFeature(models.Model):
    name = models.CharField(_('نام ویژگی'), max_length=100)
    icon = models.CharField(_('آیکون'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('ویژگی ملک')
        verbose_name_plural = _('ویژگی‌های ملک')

    def __str__(self):
        return self.name


# اضافه کردن به بالای فایل


# اضافه کردن مدل‌های جدید
def jalali_display(func):
    def wrapper(self):
        return func(self)
    return property(wrapper)

class Visit(models.Model):
    VISIT_STATUS = [
        ('pending', 'در انتظار'),
        ('confirmed', 'تایید شده'),
        ('cancelled', 'لغو شده'),
        ('completed', 'انجام شده')
    ]
    
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='visits',
        verbose_name=_('ملک')
    )
    visitor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='property_visits',
        verbose_name=_('بازدیدکننده')
    )
    visit_date = models.DateField(verbose_name=_('تاریخ بازدید'))
    visit_time = models.TimeField(verbose_name=_('ساعت بازدید'))
    status = models.CharField(
        max_length=20, 
        choices=VISIT_STATUS, 
        default='pending',
        verbose_name=_('وضعیت')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('توضیحات')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاریخ ایجاد')
    )

    class Meta:
        verbose_name = _('بازدید')
        verbose_name_plural = _('بازدیدها')
        ordering = ['-created_at']

    @jalali_display
    def get_jalali_date_display(self):  # تغییر نام از jalali_visit_date به get_jalali_date_display
        return jdatetime.fromgregorian(date=self.visit_date).strftime('%Y/%m/%d')


    def __str__(self):
        return f"بازدید {self.property.title} توسط {self.visitor.get_full_name()}"
class Booking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'در انتظار'),
        ('confirmed', 'تایید شده'),
        ('cancelled', 'لغو شده'),
        ('completed', 'پایان یافته')
    ]
    
    # Relations
    property = models.ForeignKey(
        'DailyRentProperty', 
        on_delete=models.CASCADE, 
        related_name='daily_bookings',  # تغییر نام ارتباط معکوس
        verbose_name=_('ملک')
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_bookings',  # تغییر نام به user_bookings
        verbose_name=_('کاربر')
    )
    
    # Fields
    check_in_date = models.DateField(_('تاریخ ورود'))
    check_out_date = models.DateField(_('تاریخ خروج'))
    guests_count = models.PositiveIntegerField(_('تعداد مهمانان'))
    total_price = models.DecimalField(_('قیمت کل'), max_digits=10, decimal_places=0)
    status = models.CharField(
        _('وضعیت'), 
        max_length=20, 
        choices=BOOKING_STATUS, 
        default='pending'
    )
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)

    class Meta:
        verbose_name = _('رزرو')
        verbose_name_plural = _('رزروها')
        ordering = ['-created_at']

    def calculate_total_price(self):
        """محاسبه قیمت کل رزرو"""
        nights = (self.check_out_date - self.check_in_date).days
        base_price = self.property.daily_price * nights
        extra_guests = max(0, self.guests_count - self.property.capacity)
        extra_charge = extra_guests * self.property.extra_person_fee * nights
        return base_price + extra_charge

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"رزرو {self.property.title} توسط {self.user.get_full_name()}"
class PropertyReview(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_reviews')
    rating = models.PositiveSmallIntegerField(
        _('امتیاز'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(_('نظر'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('نظر')
        verbose_name_plural = _('نظرات')
        ordering = ['-created_at']
