# Generated by Django 5.1.4 on 2024-12-19 20:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'ordering': ['-created_at'], 'verbose_name': 'تماس', 'verbose_name_plural': 'تماس\u200cها'},
        ),
        migrations.AlterModelOptions(
            name='faq',
            options={'ordering': ['order'], 'verbose_name': 'سوال متداول', 'verbose_name_plural': 'سوالات متداول'},
        ),
        migrations.AlterModelOptions(
            name='feedback',
            options={'ordering': ['-created_at'], 'verbose_name': 'بازخورد', 'verbose_name_plural': 'بازخوردها'},
        ),
        migrations.AlterModelOptions(
            name='newsletter',
            options={'verbose_name': 'خبرنامه', 'verbose_name_plural': 'خبرنامه\u200cها'},
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-created_at'], 'verbose_name': 'اعلان', 'verbose_name_plural': 'اعلانات'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-created_at'], 'verbose_name': 'پست', 'verbose_name_plural': 'پست\u200cها'},
        ),
        migrations.AlterModelOptions(
            name='sitesettings',
            options={'verbose_name': 'تنظیمات سایت', 'verbose_name_plural': 'تنظیمات سایت'},
        ),
        migrations.AddField(
            model_name='feedback',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='blog_notifications', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='post',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='نویسنده'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contact',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='ایمیل'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='خوانده شده'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='message',
            field=models.TextField(verbose_name='پیام'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(max_length=100, verbose_name='نام'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='subject',
            field=models.CharField(max_length=200, verbose_name='موضوع'),
        ),
        migrations.AlterField(
            model_name='faq',
            name='answer',
            field=models.TextField(verbose_name='پاسخ'),
        ),
        migrations.AlterField(
            model_name='faq',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='فعال'),
        ),
        migrations.AlterField(
            model_name='faq',
            name='order',
            field=models.PositiveIntegerField(default=0, verbose_name='ترتیب'),
        ),
        migrations.AlterField(
            model_name='faq',
            name='question',
            field=models.CharField(max_length=300, verbose_name='سوال'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='comment',
            field=models.TextField(verbose_name='نظر'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='is_approved',
            field=models.BooleanField(default=False, verbose_name='تایید شده'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='rating',
            field=models.PositiveSmallIntegerField(choices=[(1, '★'), (2, '★★'), (3, '★★★'), (4, '★★★★'), (5, '★★★★★')], verbose_name='امتیاز'),
        ),
        migrations.AlterField(
            model_name='newsletter',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='ایمیل'),
        ),
        migrations.AlterField(
            model_name='newsletter',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='فعال'),
        ),
        migrations.AlterField(
            model_name='newsletter',
            name='subscribed_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ عضویت'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='خوانده شده'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='message',
            field=models.TextField(verbose_name='پیام'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('info', 'اطلاع\u200cرسانی'), ('success', 'موفقیت'), ('warning', 'هشدار'), ('error', 'خطا')], default='info', max_length=10, verbose_name='نوع'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='title',
            field=models.CharField(max_length=200, verbose_name='عنوان'),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(verbose_name='محتوا'),
        ),
        migrations.AlterField(
            model_name='post',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد'),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='blog/', verbose_name='تصویر'),
        ),
        migrations.AlterField(
            model_name='post',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='فعال'),
        ),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(max_length=250, unique=True, verbose_name='اسلاگ'),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=200, verbose_name='عنوان'),
        ),
        migrations.AlterField(
            model_name='post',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='about_us',
            field=models.TextField(verbose_name='درباره ما'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='address',
            field=models.TextField(verbose_name='آدرس'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='contact_email',
            field=models.EmailField(max_length=254, verbose_name='ایمیل تماس'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='contact_phone',
            field=models.CharField(max_length=20, verbose_name='تلفن تماس'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='instagram',
            field=models.URLField(blank=True, verbose_name='اینستاگرام'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='privacy',
            field=models.TextField(verbose_name='حریم خصوصی'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='site_description',
            field=models.TextField(verbose_name='توضیحات سایت'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='site_name',
            field=models.CharField(max_length=100, verbose_name='نام سایت'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='telegram',
            field=models.URLField(blank=True, verbose_name='تلگرام'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='terms',
            field=models.TextField(verbose_name='شرایط و قوانین'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='whatsapp',
            field=models.URLField(blank=True, verbose_name='واتساپ'),
        ),
    ]
