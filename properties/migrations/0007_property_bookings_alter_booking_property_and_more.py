# Generated by Django 5.1.4 on 2024-12-25 21:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0006_remove_dailyrentproperty_minimum_days_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='bookings',
            field=models.ManyToManyField(blank=True, related_name='properties', to='properties.booking'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='property',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_bookings', to='properties.dailyrentproperty', verbose_name='ملک'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_bookings', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
    ]