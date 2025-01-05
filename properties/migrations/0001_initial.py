# Generated by Django 5.1.4 on 2024-12-14 12:22

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='عنوان')),
                ('description', models.TextField(verbose_name='توضیحات')),
                ('price', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='قیمت')),
                ('address', models.TextField(verbose_name='آدرس کامل')),
                ('location', models.JSONField(blank=True, null=True, verbose_name='موقعیت مکانی')),
                ('latitude', models.FloatField(blank=True, null=True, verbose_name='عرض جغرافیایی')),
                ('longitude', models.FloatField(blank=True, null=True, verbose_name='طول جغرافیایی')),
                ('area', models.PositiveIntegerField(verbose_name='متراژ')),
                ('rooms', models.PositiveSmallIntegerField(verbose_name='تعداد اتاق')),
                ('parking', models.BooleanField(default=False, verbose_name='پارکینگ')),
                ('elevator', models.BooleanField(default=False, verbose_name='آسانسور')),
                ('status', models.CharField(choices=[('available', 'در دسترس'), ('sold', 'فروخته شده'), ('rented', 'اجاره داده شده'), ('reserved', 'رزرو شده')], max_length=20, verbose_name='وضعیت')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_featured', models.BooleanField(default=False, verbose_name='ویژه')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('views_count', models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='real_properties', to=settings.AUTH_USER_MODEL, verbose_name='مالک')),
            ],
            options={
                'verbose_name': 'ملک',
                'verbose_name_plural': 'املاک',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PropertyFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='نام ویژگی')),
                ('icon', models.CharField(blank=True, max_length=50, verbose_name='آیکون')),
            ],
            options={
                'verbose_name': 'ویژگی ملک',
                'verbose_name_plural': 'ویژگی\u200cهای ملک',
            },
        ),
        migrations.CreateModel(
            name='RentProperty',
            fields=[
                ('property_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='properties.property')),
                ('property_type', models.CharField(choices=[('apartment', 'آپارتمان'), ('villa', 'ویلا'), ('office', 'دفتر کار'), ('store', 'مغازه')], max_length=20, verbose_name='نوع ملک')),
                ('district', models.CharField(max_length=100, verbose_name='منطقه')),
                ('floor', models.IntegerField(verbose_name='طبقه')),
                ('total_floors', models.IntegerField(verbose_name='تعداد کل طبقات')),
                ('storage', models.BooleanField(default=False, verbose_name='انباری')),
                ('balcony', models.BooleanField(default=False, verbose_name='بالکن')),
                ('package', models.BooleanField(default=False, verbose_name='پکیج')),
                ('security', models.BooleanField(default=False, verbose_name='نگهبانی')),
                ('pool', models.BooleanField(default=False, verbose_name='استخر')),
                ('gym', models.BooleanField(default=False, verbose_name='سالن ورزشی')),
                ('build_year', models.PositiveIntegerField(verbose_name='سال ساخت')),
                ('renovation', models.BooleanField(default=False, verbose_name='بازسازی شده')),
                ('document_type', models.CharField(max_length=100, verbose_name='نوع سند')),
                ('direction', models.CharField(max_length=50, verbose_name='جهت ساختمان')),
                ('monthly_rent', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='اجاره ماهانه')),
                ('deposit', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='ودیعه')),
                ('is_convertible', models.BooleanField(default=False, verbose_name='قابل تبدیل')),
                ('minimum_lease', models.IntegerField(default=12, verbose_name='حداقل مدت اجاره')),
                ('has_transfer_fee', models.BooleanField(default=False, verbose_name='دارای حق انتقال')),
            ],
            options={
                'verbose_name': 'ملک اجاره\u200cای',
                'verbose_name_plural': 'املاک اجاره\u200cای',
            },
            bases=('properties.property',),
        ),
        migrations.CreateModel(
            name='SaleProperty',
            fields=[
                ('property_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='properties.property')),
                ('property_type', models.CharField(choices=[('apartment', 'آپارتمان'), ('villa', 'ویلا'), ('office', 'دفتر کار'), ('store', 'مغازه')], max_length=20, verbose_name='نوع ملک')),
                ('district', models.CharField(max_length=100, verbose_name='منطقه')),
                ('floor', models.IntegerField(verbose_name='طبقه')),
                ('total_floors', models.IntegerField(verbose_name='تعداد کل طبقات')),
                ('storage', models.BooleanField(default=False, verbose_name='انباری')),
                ('balcony', models.BooleanField(default=False, verbose_name='بالکن')),
                ('package', models.BooleanField(default=False, verbose_name='پکیج')),
                ('security', models.BooleanField(default=False, verbose_name='نگهبانی')),
                ('pool', models.BooleanField(default=False, verbose_name='استخر')),
                ('gym', models.BooleanField(default=False, verbose_name='سالن ورزشی')),
                ('build_year', models.PositiveIntegerField(verbose_name='سال ساخت')),
                ('renovation', models.BooleanField(default=False, verbose_name='بازسازی شده')),
                ('document_type', models.CharField(max_length=100, verbose_name='نوع سند')),
                ('direction', models.CharField(max_length=50, verbose_name='جهت ساختمان')),
                ('total_price', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='قیمت کل')),
                ('price_per_meter', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='قیمت هر متر')),
                ('is_exchangeable', models.BooleanField(default=False, verbose_name='قابل معاوضه')),
                ('exchange_description', models.TextField(blank=True, verbose_name='توضیحات معاوضه')),
                ('is_negotiable', models.BooleanField(default=False, verbose_name='قابل مذاکره')),
            ],
            options={
                'verbose_name': 'ملک فروشی',
                'verbose_name_plural': 'املاک فروشی',
            },
            bases=('properties.property',),
        ),
        migrations.CreateModel(
            name='PropertyImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='properties/', verbose_name='تصویر')),
                ('title', models.CharField(blank=True, max_length=100, verbose_name='عنوان')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب')),
                ('is_main', models.BooleanField(default=False, verbose_name='تصویر اصلی')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='properties.property')),
            ],
            options={
                'verbose_name': 'تصویر ملک',
                'verbose_name_plural': 'تصاویر ملک',
                'ordering': ['order', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PropertyReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='امتیاز')),
                ('comment', models.TextField(verbose_name='نظر')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='properties.property')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='property_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'نظر',
                'verbose_name_plural': 'نظرات',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visit_date', models.DateField()),
                ('visit_time', models.TimeField()),
                ('status', models.CharField(choices=[('pending', 'در انتظار'), ('confirmed', 'تایید شده'), ('cancelled', 'لغو شده'), ('completed', 'انجام شده')], default='pending', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visits', to='properties.property')),
                ('visitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='property_visits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'بازدید',
                'verbose_name_plural': 'بازدیدها',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DailyRentProperty',
            fields=[
                ('property_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='properties.property')),
                ('property_type', models.CharField(choices=[('apartment', 'آپارتمان'), ('villa', 'ویلا'), ('suite', 'سوئیت')], max_length=20, verbose_name='نوع ملک')),
                ('district', models.CharField(max_length=100, verbose_name='منطقه')),
                ('floor', models.IntegerField(verbose_name='طبقه')),
                ('total_floors', models.IntegerField(verbose_name='تعداد کل طبقات')),
                ('storage', models.BooleanField(default=False, verbose_name='انباری')),
                ('balcony', models.BooleanField(default=False, verbose_name='بالکن')),
                ('package', models.BooleanField(default=False, verbose_name='پکیج')),
                ('security', models.BooleanField(default=False, verbose_name='نگهبانی')),
                ('pool', models.BooleanField(default=False, verbose_name='استخر')),
                ('gym', models.BooleanField(default=False, verbose_name='سالن ورزشی')),
                ('build_year', models.PositiveIntegerField(verbose_name='سال ساخت')),
                ('renovation', models.BooleanField(default=False, verbose_name='بازسازی شده')),
                ('document_type', models.CharField(max_length=100, verbose_name='نوع سند')),
                ('direction', models.CharField(max_length=50, verbose_name='جهت ساختمان')),
                ('daily_price', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='قیمت روزانه')),
                ('minimum_days', models.IntegerField(default=1, verbose_name='حداقل مدت اقامت')),
                ('maximum_days', models.IntegerField(blank=True, null=True, verbose_name='حداکثر مدت اقامت')),
                ('capacity', models.PositiveIntegerField(default=2, verbose_name='ظرفیت')),
                ('min_stay', models.PositiveIntegerField(default=1, verbose_name='حداقل مدت اقامت')),
                ('max_guests', models.PositiveIntegerField(default=2, verbose_name='حداکثر تعداد مهمان')),
                ('extra_person_fee', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True, verbose_name='هزینه نفر اضافه')),
                ('check_in_time', models.TimeField(verbose_name='ساعت ورود')),
                ('check_out_time', models.TimeField(verbose_name='ساعت خروج')),
                ('favorites', models.ManyToManyField(blank=True, related_name='favorite_dailies', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'ملک اجاره روزانه',
                'verbose_name_plural': 'املاک اجاره روزانه',
            },
            bases=('properties.property',),
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in_date', models.DateField(verbose_name='تاریخ ورود')),
                ('check_out_date', models.DateField(verbose_name='تاریخ خروج')),
                ('guests_count', models.PositiveIntegerField(verbose_name='تعداد مهمانان')),
                ('total_price', models.DecimalField(decimal_places=0, max_digits=10, verbose_name='قیمت کل')),
                ('status', models.CharField(choices=[('pending', 'در انتظار'), ('confirmed', 'تایید شده'), ('cancelled', 'لغو شده'), ('completed', 'پایان یافته')], default='pending', max_length=20, verbose_name='وضعیت')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='property_bookings', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='properties.dailyrentproperty', verbose_name='ملک')),
            ],
            options={
                'verbose_name': 'رزرو',
                'verbose_name_plural': 'رزروها',
                'ordering': ['-created_at'],
            },
        ),
    ]