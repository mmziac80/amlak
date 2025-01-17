# Generated by Django 5.1.4 on 2024-12-22 19:11

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_alter_property_latitude_alter_property_longitude'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='آدرس کامل'),
        ),
        migrations.AlterField(
            model_name='property',
            name='area',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='متراژ'),
        ),
        migrations.AlterField(
            model_name='property',
            name='deal_type',
            field=models.CharField(blank=True, choices=[('sale', 'فروش'), ('rent', 'اجاره'), ('daily', 'اجاره روزانه')], default='rent', max_length=10, null=True, verbose_name='نوع معامله'),
        ),
        migrations.AlterField(
            model_name='property',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='توضیحات'),
        ),
        migrations.AlterField(
            model_name='property',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)]),
        ),
        migrations.AlterField(
            model_name='property',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)]),
        ),
        migrations.AlterField(
            model_name='property',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='real_properties', to=settings.AUTH_USER_MODEL, verbose_name='مالک'),
        ),
        migrations.AlterField(
            model_name='property',
            name='rooms',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='تعداد اتاق'),
        ),
        migrations.AlterField(
            model_name='property',
            name='status',
            field=models.CharField(blank=True, choices=[('available', 'در دسترس'), ('sold', 'فروخته شده'), ('rented', 'اجاره داده شده'), ('reserved', 'رزرو شده')], max_length=20, null=True, verbose_name='وضعیت'),
        ),
        migrations.AlterField(
            model_name='property',
            name='title',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='عنوان'),
        ),
    ]
