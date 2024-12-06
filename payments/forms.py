from django import forms
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Payment, RefundRequest
from .constants import PAYMENT_STATUS
from .validators import (
    PaymentAmountValidator,
    BankAccountValidator, 
    validate_refund_reason
)

class PaymentInitiateForm(forms.ModelForm):
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'تاریخ ورود'
        })
    )
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control',
            'placeholder': 'تاریخ خروج'
        })
    )

    class Meta:
        model = Payment
        fields = ['check_in_date', 'check_out_date']

    def __init__(self, *args, **kwargs):
        self.property = kwargs.pop('property')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out:
            # تاریخ ورود نباید قبل از امروز باشد
            if check_in < timezone.now().date():
                raise forms.ValidationError('تاریخ ورود نمی‌تواند در گذشته باشد')

            # تاریخ ورود باید قبل از خروج باشد
            if check_in >= check_out:
                raise forms.ValidationError('تاریخ ورود باید قبل از تاریخ خروج باشد')
            
            # بررسی رزرو بودن تاریخ‌ها
            if self.property.is_reserved(check_in, check_out):
                raise forms.ValidationError('این تاریخ‌ها قبلاً رزرو شده است')
            
            # محاسبه تعداد روزها و قیمت کل
            days = (check_out - check_in).days
            total_amount = self.property.daily_price * days
            cleaned_data['total_amount'] = total_amount
            
        return cleaned_data

class PaymentConfirmForm(forms.Form):
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
    status = forms.ChoiceField(
        choices=[('', 'همه')] + list(PAYMENT_STATUS.items()),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
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
    class Meta:
        model = RefundRequest
        fields = ['reason', 'bank_account']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'دلیل درخواست استرداد را وارد کنید'
            }),
            'bank_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره شبا را وارد کنید'
            })
        }

    def clean_reason(self):
        reason = self.cleaned_data['reason']
        validate_refund_reason(reason)
        return reason

    def clean_bank_account(self):
        bank_account = self.cleaned_data['bank_account']
        validator = BankAccountValidator()
        validator(bank_account)
        return bank_account
