# Generated by Django 5.1.4 on 2024-12-19 20:48

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settlements', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auditlog',
            options={'ordering': ['-timestamp'], 'verbose_name': 'گزارش تغییرات', 'verbose_name_plural': 'گزارش\u200cهای تغییرات'},
        ),
        migrations.AlterModelOptions(
            name='settlement',
            options={'ordering': ['-created_at'], 'verbose_name': 'تسویه حساب', 'verbose_name_plural': 'تسویه حساب\u200cها'},
        ),
        migrations.AddField(
            model_name='auditlog',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AddField(
            model_name='settlement',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='settlements', to=settings.AUTH_USER_MODEL, verbose_name='مالک'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='settlement',
            name='processed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_settlements', to=settings.AUTH_USER_MODEL, verbose_name='بررسی شده توسط'),
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='action',
            field=models.CharField(max_length=50, verbose_name='عملیات'),
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='details',
            field=models.JSONField(blank=True, null=True, verbose_name='جزئیات'),
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='ip_address',
            field=models.GenericIPAddressField(verbose_name='آدرس IP'),
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='object_id',
            field=models.IntegerField(null=True, verbose_name='شناسه شیء'),
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, verbose_name='زمان'),
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='user_agent',
            field=models.CharField(max_length=500, verbose_name='مرورگر کاربر'),
        ),
        migrations.AlterField(
            model_name='settlement',
            name='amount',
            field=models.DecimalField(decimal_places=0, max_digits=12, validators=[django.core.validators.MinValueValidator(50000)], verbose_name='مبلغ'),
        ),
        migrations.AlterField(
            model_name='settlement',
            name='bank_account',
            field=models.CharField(max_length=26, verbose_name='شماره شبا'),
        ),
        migrations.AlterField(
            model_name='settlement',
            name='bank_reference_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='شناسه پیگیری بانکی'),
        ),
        migrations.AlterField(
            model_name='settlement',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد'),
        ),
        migrations.AlterField(
            model_name='settlement',
            name='rejection_reason',
            field=models.TextField(blank=True, verbose_name='دلیل رد درخواست'),
        ),
        migrations.AlterField(
            model_name='settlement',
            name='settled_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تسویه'),
        ),
        migrations.AlterField(
            model_name='settlement',
            name='status',
            field=models.CharField(choices=[('pending', 'در انتظار تایید'), ('processing', 'در حال پردازش'), ('completed', 'تکمیل شده'), ('failed', 'ناموفق'), ('rejected', 'رد شده'), ('cancelled', 'لغو شده')], default='pending', max_length=20, verbose_name='وضعیت'),
        ),
        migrations.AlterField(
            model_name='settlement',
            name='tracking_code',
            field=models.CharField(editable=False, max_length=32, unique=True, verbose_name='کد پیگیری'),
        ),
        migrations.AlterField(
            model_name='settlement',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['user', 'action'], name='settlements_user_id_be0205_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['timestamp'], name='settlements_timesta_5e8d3f_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['ip_address'], name='settlements_ip_addr_e0e430_idx'),
        ),
        migrations.AddIndex(
            model_name='settlement',
            index=models.Index(fields=['tracking_code'], name='settlements_trackin_e26be5_idx'),
        ),
        migrations.AddIndex(
            model_name='settlement',
            index=models.Index(fields=['status', 'created_at'], name='settlements_status_8c7d7a_idx'),
        ),
        migrations.AddIndex(
            model_name='settlement',
            index=models.Index(fields=['owner', 'status'], name='settlements_owner_i_ecf942_idx'),
        ),
        migrations.AddIndex(
            model_name='settlement',
            index=models.Index(fields=['bank_reference_id'], name='settlements_bank_re_aa914a_idx'),
        ),
    ]
