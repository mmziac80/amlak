# Generated by Django 5.1.4 on 2024-12-19 20:48

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['-date_joined'], 'verbose_name': 'کاربر', 'verbose_name_plural': 'کاربران'},
        ),
        migrations.AlterModelOptions(
            name='useractivity',
            options={'ordering': ['-created_at'], 'verbose_name': 'فعالیت کاربر', 'verbose_name_plural': 'فعالیت\u200cهای کاربر'},
        ),
        migrations.AlterModelOptions(
            name='userdevice',
            options={'ordering': ['-last_login'], 'verbose_name': 'دستگاه کاربر', 'verbose_name_plural': 'دستگاه\u200cهای کاربر'},
        ),
        migrations.AlterModelOptions(
            name='usernotification',
            options={'ordering': ['-created_at'], 'verbose_name': 'اعلان کاربر', 'verbose_name_plural': 'اعلان\u200cهای کاربر'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'پروفایل کاربر', 'verbose_name_plural': 'پروفایل\u200cهای کاربر'},
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='تصویر پروفایل'),
        ),
        migrations.AlterField(
            model_name='user',
            name='bank_account',
            field=models.CharField(blank=True, help_text='شماره شبا بدون حروف اضافه', max_length=26, verbose_name='شماره شبا'),
        ),
        migrations.AlterField(
            model_name='user',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='تاریخ تولد'),
        ),
        migrations.AlterField(
            model_name='user',
            name='identity_document',
            field=models.FileField(blank=True, null=True, upload_to='identity_docs/', verbose_name='مدارک هویتی'),
        ),
        migrations.AlterField(
            model_name='user',
            name='identity_verified',
            field=models.BooleanField(default=False, verbose_name='هویت تایید شده'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_email_verified',
            field=models.BooleanField(default=False, verbose_name='ایمیل تایید شده'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_phone_verified',
            field=models.BooleanField(default=False, verbose_name='تایید شده'),
        ),
        migrations.AlterField(
            model_name='user',
            name='national_code',
            field=models.CharField(max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='کد ملی باید 10 رقم باشد', regex='^\\d{10}$')], verbose_name='کد ملی'),
        ),
        migrations.AlterField(
            model_name='user',
            name='otp',
            field=models.CharField(blank=True, max_length=6, verbose_name='کد تایید موقت'),
        ),
        migrations.AlterField(
            model_name='user',
            name='otp_create_time',
            field=models.DateTimeField(null=True, verbose_name='تاریخ ایجاد کد'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=11, unique=True, validators=[django.core.validators.RegexValidator(message='شماره موبایل باید در قالب 09123456789 باشد', regex='^09\\d{9}$')], verbose_name='شماره موبایل'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'مدیر'), ('agent', 'مشاور املاک'), ('owner', 'صاحب ملک'), ('user', 'کاربر عادی')], default='user', max_length=10, verbose_name='نوع کاربر'),
        ),
        migrations.AlterField(
            model_name='useractivity',
            name='activity_type',
            field=models.CharField(choices=[('login', 'ورود'), ('logout', 'خروج'), ('profile_update', 'بروزرسانی پروفایل'), ('password_change', 'تغییر رمز عبور'), ('verification', 'تایید شماره موبایل')], max_length=20, verbose_name='نوع فعالیت'),
        ),
        migrations.AlterField(
            model_name='useractivity',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد'),
        ),
        migrations.AlterField(
            model_name='useractivity',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='آدرس IP'),
        ),
        migrations.AlterField(
            model_name='useractivity',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='useractivity',
            name='user_agent',
            field=models.CharField(blank=True, max_length=200, verbose_name='مرورگر کاربر'),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='device_id',
            field=models.CharField(max_length=200, unique=True, verbose_name='شناسه دستگاه'),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='device_type',
            field=models.CharField(choices=[('web', 'مرورگر'), ('android', 'اندروید'), ('ios', 'آیفون')], max_length=10, verbose_name='نوع دستگاه'),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='فعال'),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='last_login',
            field=models.DateTimeField(auto_now=True, verbose_name='آخرین ورود'),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='push_token',
            field=models.CharField(blank=True, max_length=200, verbose_name='توکن نوتیفیکیشن'),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devices', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد'),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='خوانده شده'),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='link',
            field=models.URLField(blank=True, verbose_name='لینک'),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='message',
            field=models.TextField(verbose_name='متن پیام'),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='notification_type',
            field=models.CharField(choices=[('payment', 'پرداخت'), ('booking', 'رزرو'), ('message', 'پیام'), ('system', 'سیستمی')], max_length=20, verbose_name='نوع اعلان'),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='title',
            field=models.CharField(max_length=200, verbose_name='عنوان'),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True, verbose_name='درباره من'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='company',
            field=models.CharField(blank=True, max_length=100, verbose_name='شرکت/آژانس'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'مرد'), ('F', 'زن')], max_length=1, verbose_name='جنسیت'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='website',
            field=models.URLField(blank=True, verbose_name='وبسایت'),
        ),
    ]
