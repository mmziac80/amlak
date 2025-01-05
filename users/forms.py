# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile

class SignUpForm(UserCreationForm):
    """فرم ثبت‌نام کاربر جدید"""
    phone = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '09123456789'
        })
    )
    
    national_code = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد ملی'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'phone', 'national_code', 'password1', 'password2')

class UserProfileForm(forms.ModelForm):
    """فرم ویرایش پروفایل کاربر"""
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    bank_account = forms.CharField(
        max_length=26,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'شماره شبا'
        })
    )

    class Meta:
        model = UserProfile
        fields = (
            'gender', 'bio', 'website', 'company'
        )
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'})
        }

class IdentityVerificationForm(forms.Form):
    """فرم احراز هویت"""
    identity_document = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text=_('تصویر کارت ملی یا شناسنامه خود را آپلود کنید')
    )
class PhoneLoginForm(forms.Form):
    phone = forms.CharField(
        label=_('شماره موبایل'),
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '09123456789',
            'dir': 'ltr'
        })
    )

class OTPVerifyForm(forms.Form):
    otp = forms.CharField(
        label=_('کد تایید'),
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد تایید را وارد کنید',
            'dir': 'ltr'
        })
    )
