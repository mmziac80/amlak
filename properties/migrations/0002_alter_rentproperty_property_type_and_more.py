# Generated by Django 5.1.3 on 2024-11-29 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rentproperty',
            name='property_type',
            field=models.CharField(choices=[('apartment', 'آپارتمان'), ('villa', 'ویلا'), ('commercial', 'تجاری')], max_length=20, verbose_name='نوع ملک'),
        ),
        migrations.AlterField(
            model_name='saleproperty',
            name='property_type',
            field=models.CharField(choices=[('apartment', 'آپارتمان'), ('villa', 'ویلا'), ('commercial', 'تجاری')], max_length=20, verbose_name='نوع ملک'),
        ),
    ]
