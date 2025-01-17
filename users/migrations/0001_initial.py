# Generated by Django 5.1.4 on 2024-12-12 19:38

import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import users.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone', models.CharField(max_length=11, unique=True, validators=[django.core.validators.RegexValidator(message='????? ?????? ???? ?? ???? 09123456789 ????', regex='^09\\d{9}$')], verbose_name='????? ??????')),
                ('national_code', models.CharField(max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='?? ??? ???? 10 ??? ????', regex='^\\d{10}$')], verbose_name='?? ???')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='????? ????')),
                ('role', models.CharField(choices=[('admin', '?????'), ('agent', '????? ?????'), ('owner', '???? ???'), ('user', '????? ????')], default='user', max_length=10, verbose_name='??? ?????')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='????? ???????')),
                ('identity_document', models.FileField(blank=True, null=True, upload_to='identity_docs/', verbose_name='????? ?????')),
                ('is_phone_verified', models.BooleanField(default=False, verbose_name='????? ???')),
                ('is_email_verified', models.BooleanField(default=False, verbose_name='????? ????? ???')),
                ('identity_verified', models.BooleanField(default=False, verbose_name='????? ???? ???')),
                ('otp', models.CharField(blank=True, max_length=6, verbose_name='?? ????? ????')),
                ('otp_create_time', models.DateTimeField(null=True, verbose_name='????? ?????? ??')),
                ('email_verification_token', models.CharField(blank=True, max_length=100)),
                ('bank_account', models.CharField(blank=True, help_text='????? ??? ???? ????? ????', max_length=26, verbose_name='????? ???')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '?????',
                'verbose_name_plural': '???????',
                'ordering': ['-date_joined'],
            },
            managers=[
                ('objects', users.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('login', '????'), ('logout', '????'), ('profile_update', '????????? ???????'), ('password_change', '????? ??? ????'), ('verification', '????? ????? ??????')], max_length=20, verbose_name='??? ??????')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='???? IP')),
                ('user_agent', models.CharField(blank=True, max_length=200, verbose_name='?????? ?????')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='????? ?????')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to=settings.AUTH_USER_MODEL, verbose_name='?????')),
            ],
            options={
                'verbose_name': '?????? ?????',
                'verbose_name_plural': '?????????? ?????',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_type', models.CharField(choices=[('web', '??????'), ('android', '???????'), ('ios', '?????')], max_length=10, verbose_name='??? ??????')),
                ('device_id', models.CharField(max_length=200, unique=True, verbose_name='????? ??????')),
                ('push_token', models.CharField(blank=True, max_length=200, verbose_name='???? ??????????')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='????? ????')),
                ('is_active', models.BooleanField(default=True, verbose_name='????')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devices', to=settings.AUTH_USER_MODEL, verbose_name='?????')),
            ],
            options={
                'verbose_name': '?????? ?????',
                'verbose_name_plural': '?????????? ?????',
                'ordering': ['-last_login'],
            },
        ),
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('payment', '??????'), ('booking', '????'), ('message', '????'), ('system', '??????')], max_length=20, verbose_name='??? ?????')),
                ('title', models.CharField(max_length=200, verbose_name='?????')),
                ('message', models.TextField(verbose_name='??? ????')),
                ('link', models.URLField(blank=True, verbose_name='????')),
                ('is_read', models.BooleanField(default=False, verbose_name='?????? ???')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='????? ?????')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='?????')),
            ],
            options={
                'verbose_name': '????? ?????',
                'verbose_name_plural': '????????? ?????',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(blank=True, choices=[('M', '???'), ('F', '??')], max_length=1, verbose_name='?????')),
                ('bio', models.TextField(blank=True, verbose_name='?????? ??')),
                ('website', models.URLField(blank=True, verbose_name='??????')),
                ('company', models.CharField(blank=True, max_length=100, verbose_name='????/?????')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='?????')),
            ],
            options={
                'verbose_name': '??????? ?????',
                'verbose_name_plural': '??????????? ?????',
            },
        ),
    ]
