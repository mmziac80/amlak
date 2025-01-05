# -*- coding: utf-8 -*-
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Payment, RefundRequest
from .constants import PAYMENT_STATUS
from .validators import (
    PaymentAmountValidator,
    BankAccountValidator
)
class PaymentInitiateForm(forms.ModelForm):
    """فرم شروع پرداخت"""
    check_in_date = forms.DateField(
        label=_('تاریخ ورود'),
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    check_out_date = forms.DateField(
        label=_('تاریخ خروج'),
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control'
        })
    )

    class Meta:
        model = Payment
        fields = ['check_in_date', 'check_out_date']

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out:
            if check_in < timezone.now().date():
                raise forms.ValidationError('تاریخ ورود نمی‌تواند در گذشته باشد')

            if check_in >= check_out:
                raise forms.ValidationError('تاریخ ورود باید قبل از تاریخ خروج باشد')
            
            if self.property.is_reserved(check_in, check_out):
                raise forms.ValidationError('این تاریخ‌ها قبلاً رزرو شده است')
            
            days = (check_out - check_in).days
            total_amount = self.property.daily_price * days
            cleaned_data['total_amount'] = total_amount
            
        return cleaned_data
class PaymentConfirmForm(forms.Form):
    """فرم تایید پرداخت"""
    terms_accepted = forms.BooleanField(
        required=True,
        label='قوانین و مقررات را می‌پذیرم',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean_terms_accepted(self):
        if not self.cleaned_data['terms_accepted']:
            raise forms.ValidationError('پذیرش قوانین و مقررات الزامی است')
        return self.cleaned_data['terms_accepted']
class PaymentFilterForm(forms.Form):
    """فرم فیلتر پرداخت‌ها"""
    status = forms.ChoiceField(
        choices=[('', 'همه')] + list(PAYMENT_STATUS.items()),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_amount = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'حداقل مبلغ'
        })
    )
    
    max_amount = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'حداکثر مبلغ'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
class RefundRequestForm(forms.ModelForm):
    """فرم درخواست استرداد وجه"""
    class Meta:
        model = RefundRequest
        fields = ['reason', 'bank_account']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'دلیل درخواست استرداد را شرح دهید'
            }),
            'bank_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':  'شماره شبا را وارد کنید'
            })
        }

    def clean_bank_account(self):
        bank_account = self.cleaned_data['bank_account']
        validator = BankAccountValidator()
        validator(bank_account)
        return bank_account
