# نوع ملک
PROPERTY_TYPE_CHOICES = [
    ('apartment', 'آپارتمان'),
    ('villa', 'ویلا'),
    ('office', 'دفتر کار'),
    ('store', 'مغازه'),
    ('land', 'زمین'),
    ('garden', 'باغ'),
    ('warehouse', 'انبار'),
]

# مناطق شهری
DISTRICT_CHOICES = [
    ('1', 'منطقه ۱'),
    ('2', 'منطقه ۲'),
    ('3', 'منطقه ۳'),
    ('4', 'منطقه ۴'),
    ('5', 'منطقه ۵'),
    ('6', 'منطقه ۶'),
    ('7', 'منطقه ۷'),
    ('8', 'منطقه ۸'),
    ('9', 'منطقه ۹'),
    ('10', 'منطقه ۱۰'),
]

# نوع سند
DOCUMENT_TYPE_CHOICES = [
    ('registered', 'سند ثبتی'),
    ('detailed', 'سند تفکیکی'),
    ('preliminary', 'قولنامه‌ای'),
    ('endowment', 'وقفی'),
]

# جهت ساختمان
DIRECTION_CHOICES = [
    ('north', 'شمالی'),
    ('south', 'جنوبی'),
    ('east', 'شرقی'),
    ('west', 'غربی'),
]

# وضعیت ملک
PROPERTY_STATUS_CHOICES = [
    ('available', 'قابل معامله'),
    ('reserved', 'رزرو شده'),
    ('sold', 'فروخته شده'),
    ('rented', 'اجاره داده شده'),
]

# نوع کاربری
USAGE_TYPE_CHOICES = [
    ('residential', 'مسکونی'),
    ('commercial', 'تجاری'),
    ('office', 'اداری'),
    ('industrial', 'صنعتی'),
]

# امکانات ملک
FACILITY_CHOICES = [
    ('parking', 'پارکینگ'),
    ('elevator', 'آسانسور'),
    ('storage', 'انباری'),
    ('balcony', 'بالکن'),
    ('package', 'پکیج'),
    ('security', 'نگهبانی'),
    ('pool', 'استخر'),
    ('gym', 'سالن ورزشی'),
    ('garden', 'فضای سبز'),
    ('lobby', 'لابی'),
    ('cctv', 'دوربین مداربسته'),
    ('doorman', 'سرایدار'),
]

# وضعیت بازدید
VISIT_STATUS_CHOICES = [
    ('pending', 'در انتظار تایید'),
    ('approved', 'تایید شده'),
    ('rejected', 'رد شده'),
    ('completed', 'انجام شده'),
    ('canceled', 'لغو شده'),
]

# وضعیت رزرو
BOOKING_STATUS_CHOICES = [
    ('pending', 'در انتظار پرداخت'),
    ('confirmed', 'تایید شده'),
    ('canceled', 'لغو شده'),
    ('completed', 'پایان یافته'),
]

# نوع معامله
DEAL_TYPE_CHOICES = [
    ('sale', 'فروش'),
    ('rent', 'اجاره'),
    ('daily', 'اجاره روزانه'),
]

# نوع مرتب‌سازی
SORT_CHOICES = [
    ('price_asc', 'قیمت: کم به زیاد'),
    ('price_desc', 'قیمت: زیاد به کم'),
    ('area_asc', 'متراژ: کم به زیاد'),
    ('area_desc', 'متراژ: زیاد به کم'),
    ('date_desc', 'جدیدترین'),
    ('date_asc', 'قدیمی‌ترین'),
]
