from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils.text import slugify

class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'آپارتمان'),
        ('villa', 'ویلا'),
        ('office', 'دفتر کار'),
        ('store', 'مغازه'),
        ('land', 'زمین'),
    ]
    
    DISTRICT_CHOICES = [
        ('1', 'منطقه ۱'),
        ('2', 'منطقه ۲'),
        ('3', 'منطقه ۳'),
        ('4', 'منطقه ۴'),
        ('5', 'منطقه ۵'),
        ('6', 'منطقه ۶'),
        ('7', 'منطقه ۷'),
        ('8', 'منطقه ۸'),
    ]

    title = models.CharField(_('عنوان'), max_length=200)
    slug = models.SlugField(_('اسلاگ'), max_length=250, unique=True, allow_unicode=True)
    description = models.TextField(_('توضیحات'))
    property_type = models.CharField(_('نوع ملک'), max_length=20, choices=PROPERTY_TYPE_CHOICES)
    district = models.CharField(_('منطقه'), max_length=2, choices=DISTRICT_CHOICES)
    address = models.TextField(_('آدرس'))
    area = models.PositiveIntegerField(_('متراژ'), validators=[MinValueValidator(1)])
    rooms = models.PositiveSmallIntegerField(_('تعداد اتاق'))
    floor = models.PositiveSmallIntegerField(_('طبقه'))
    total_floors = models.PositiveSmallIntegerField(_('تعداد کل طبقات'))
    
    # امکانات
    parking = models.BooleanField(_('پارکینگ'), default=False)
    elevator = models.BooleanField(_('آسانسور'), default=False)
    storage = models.BooleanField(_('انباری'), default=False)
    balcony = models.BooleanField(_('بالکن'), default=False)
    package = models.BooleanField(_('پکیج'), default=False)
    security = models.BooleanField(_('نگهبان'), default=False)
    pool = models.BooleanField(_('استخر'), default=False)
    gym = models.BooleanField(_('سالن ورزشی'), default=False)
    
    # مشخصات ساختمان
    build_year = models.PositiveSmallIntegerField(_('سال ساخت'), null=True, blank=True)
    renovation = models.BooleanField(_('بازسازی شده'), default=False)
    document_type = models.CharField(_('نوع سند'), max_length=50, blank=True)
    direction = models.CharField(_('جهت ساختمان'), max_length=50, blank=True)
    
    # وضعیت
    is_active = models.BooleanField(_('فعال'), default=True)
    is_verified = models.BooleanField(_('تایید شده'), default=False)
    
    # روابط
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='properties',
        verbose_name=_('مالک')
    )
    
    # زمان‌ها
    created_at = models.DateTimeField(_('تاریخ ثبت'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    verified_at = models.DateTimeField(_('تاریخ تایید'), null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.get_district_display()}"

class SaleProperty(Property):
    price = models.DecimalField(
        _('قیمت'), 
        max_digits=12, 
        decimal_places=0,
        validators=[MinValueValidator(0)]
    )
    price_per_meter = models.DecimalField(
        _('قیمت هر متر'), 
        max_digits=12, 
        decimal_places=0,
        validators=[MinValueValidator(0)]
    )
    is_exchangeable = models.BooleanField(_('قابل معاوضه'), default=False)
    is_negotiable = models.BooleanField(_('قابل مذاکره'), default=True)
    exchange_description = models.TextField(_('توضیحات معاوضه'), blank=True)

    class Meta:
        verbose_name = _('ملک فروشی')
        verbose_name_plural = _('املاک فروشی')
        ordering = ['-created_at']

class RentProperty(Property):
    monthly_rent = models.DecimalField(
        _('اجاره ماهیانه'), 
        max_digits=12, 
        decimal_places=0,
        validators=[MinValueValidator(0)]
    )
    deposit = models.DecimalField(
        _('ودیعه'), 
        max_digits=12, 
        decimal_places=0,
        validators=[MinValueValidator(0)]
    )
    is_convertible = models.BooleanField(_('قابل تبدیل'), default=False)
    minimum_lease = models.PositiveSmallIntegerField(_('حداقل مدت اجاره'), default=12)
    has_transfer_fee = models.BooleanField(_('حق انتقال دارد'), default=False)

    class Meta:
        verbose_name = _('ملک اجاره‌ای')
        verbose_name_plural = _('املاک اجاره‌ای')
        ordering = ['-created_at']

class PropertyImage(models.Model):
    property = models.ForeignKey(
        'Property', 
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('ملک')
    )
    image = models.ImageField(_('تصویر'), upload_to='properties/%Y/%m/')
    title = models.CharField(_('عنوان'), max_length=100, blank=True)
    is_main = models.BooleanField(_('تصویر اصلی'), default=False)
    order = models.PositiveSmallIntegerField(_('ترتیب'), default=0)
    created_at = models.DateTimeField(_('تاریخ ثبت'), auto_now_add=True)

    class Meta:
        verbose_name = _('تصویر ملک')
        verbose_name_plural = _('تصاویر ملک')
        ordering = ['order', '-is_main', '-created_at']

    def __str__(self):
        return f"تصویر {self.property.title}"

class PropertyFeature(models.Model):
    property = models.ForeignKey(
        'Property',
        on_delete=models.CASCADE,
        related_name='features',
        verbose_name=_('ملک')
    )
    title = models.CharField(_('عنوان'), max_length=100)
    value = models.CharField(_('مقدار'), max_length=200)
    icon = models.CharField(_('آیکون'), max_length=50, blank=True)
    order = models.PositiveSmallIntegerField(_('ترتیب'), default=0)

    class Meta:
        verbose_name = _('ویژگی ملک')
        verbose_name_plural = _('ویژگی‌های ملک')
        ordering = ['order']

    def __str__(self):
        return f"{self.title}: {self.value}"

# به انتهای فایل models.py اضافه کنید

class DailyRentProperty(Property):
    daily_price = models.DecimalField(
        _('قیمت روزانه'), 
        max_digits=12, 
        decimal_places=0,
        validators=[MinValueValidator(0)]
    )
    minimum_days = models.PositiveSmallIntegerField(_('حداقل مدت اقامت'), default=1)
    maximum_days = models.PositiveSmallIntegerField(_('حداکثر مدت اقامت'), null=True, blank=True)
    capacity = models.PositiveSmallIntegerField(_('ظرفیت'), default=2)
    extra_person_fee = models.DecimalField(
        _('هزینه نفر اضافه'),
        max_digits=10,
        decimal_places=0,
        default=0
    )

    class Meta:
        verbose_name = _('ملک اجاره روزانه')
        verbose_name_plural = _('املاک اجاره روزانه')
        ordering = ['-created_at']

# به انتهای فایل models.py اضافه کنید

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('confirmed', 'تایید شده'),
        ('cancelled', 'لغو شده'),
        ('completed', 'تکمیل شده')
    ]

    property = models.ForeignKey(
        'Property',
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('ملک')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('کاربر')
    )
    check_in_date = models.DateField(_('تاریخ ورود'))
    check_out_date = models.DateField(_('تاریخ خروج'))
    guests_count = models.PositiveSmallIntegerField(_('تعداد مهمان‌ها'), default=1)
    total_price = models.DecimalField(_('مبلغ کل'), max_digits=12, decimal_places=0)
    status = models.CharField(_('وضعیت'), max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.BooleanField(_('وضعیت پرداخت'), default=False)
    
    created_at = models.DateTimeField(_('تاریخ ثبت'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('رزرو')
        verbose_name_plural = _('رزروها')
        ordering = ['-created_at']

    def __str__(self):
        return f"رزرو {self.property.title} توسط {self.user.get_full_name()}"

# به انتهای فایل models.py اضافه کنید

class PropertyAvailability(models.Model):
    property = models.ForeignKey(
        'Property',
        on_delete=models.CASCADE,
        related_name='availabilities',
        verbose_name=_('ملک')
    )
    start_date = models.DateField(_('تاریخ شروع'))
    end_date = models.DateField(_('تاریخ پایان'))
    is_available = models.BooleanField(_('در دسترس'), default=True)
    price_adjustment = models.DecimalField(
        _('تنظیم قیمت'), 
        max_digits=5, 
        decimal_places=2,
        default=1.00,
        help_text=_('ضریب تغییر قیمت در این بازه (مثلا 1.2 برای 20٪ افزایش)')
    )
    note = models.TextField(_('یادداشت'), blank=True)
    created_at = models.DateTimeField(_('تاریخ ثبت'), auto_now_add=True)

    class Meta:
        verbose_name = _('زمان در دسترس')
        verbose_name_plural = _('زمان‌های در دسترس')
        ordering = ['start_date']

    def __str__(self):
        return f"{self.property.title} - از {self.start_date} تا {self.end_date}"

# به انتهای فایل models.py اضافه کنید

class Visit(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('confirmed', 'تایید شده'),
        ('cancelled', 'لغو شده'),
        ('completed', 'انجام شده')
    ]

    property = models.ForeignKey(
        'Property',
        on_delete=models.CASCADE,
        related_name='visits',
        verbose_name=_('ملک')
    )
    visitor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='property_visits',
        verbose_name=_('بازدیدکننده')
    )
    visit_date = models.DateField(_('تاریخ بازدید'))
    visit_time = models.TimeField(_('ساعت بازدید'))
    status = models.CharField(_('وضعیت'), max_length=20, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(_('توضیحات'), blank=True)
    created_at = models.DateTimeField(_('تاریخ ثبت'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('بازدید')
        verbose_name_plural = _('بازدیدها')
        ordering = ['-created_at']

    def __str__(self):
        return f"بازدید {self.property.title} - {self.visitor.get_full_name()}"
