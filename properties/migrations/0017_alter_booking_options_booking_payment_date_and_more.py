# Generated by Django 5.1.3 on 2024-12-03 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0016_booking_propertyavailability'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'ordering': ['-created_at'], 'verbose_name': 'رزرو', 'verbose_name_plural': 'رزروها'},
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='تاریخ پرداخت'),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='شناسه پرداخت'),
        ),
        migrations.AddField(
            model_name='propertyavailability',
            name='price_adjustment',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True, verbose_name='تنظیم قیمت'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('pending', 'در انتظار تایید'), ('confirmed', 'تایید شده'), ('paid', 'پرداخت شده'), ('cancelled', 'لغو شده')], default='pending', max_length=20, verbose_name='وضعیت'),
        ),
        migrations.AlterField(
            model_name='propertyavailability',
            name='is_available',
            field=models.BooleanField(default=True, verbose_name='قابل رزرو'),
        ),
        migrations.AlterUniqueTogether(
            name='propertyavailability',
            unique_together={('property', 'date')},
        ),
    ]
