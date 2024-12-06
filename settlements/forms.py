from django import forms
from django.utils import timezone
from django.core.validators import MinValueValidator
from .models import Settlement
from .validators import PaymentAmountValidator, BankAccountValidator

class SettlementCreateForm(forms.ModelForm):
    confirm_terms = forms.BooleanField(
        required=True,
        label='قوانین و مقررات را می‌پذیرم',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Settlement
        fields = ['amount', 'bank_account', 'confirm_terms']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مبلغ به تومان',
                'min': '50000'
            }),
            'bank_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'IR شماره شبا - شروع با',
                'dir': 'ltr',
                'pattern': '^IR[0-9]{24}$'
            })
        }
        
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        validator = PaymentAmountValidator()
        validator(amount)
        
        # بررسی محدودیت‌های تسویه
        min_amount = 50000
        max_amount = 50000000
        if amount < min_amount:
            raise forms.ValidationError(f'حداقل مبلغ تسویه {min_amount:,} تومان است')
        if amount > max_amount:
            raise forms.ValidationError(f'حداکثر مبلغ تسویه {max_amount:,} تومان است')
            
        return amount

    def clean_bank_account(self):
        bank_account = self.cleaned_data['bank_account']
        validator = BankAccountValidator()
        validator(bank_account)
        return bank_account

class SettlementFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        label='از تاریخ',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        label='تا تاریخ',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'همه')] + Settlement.STATUS_CHOICES,
        required=False,
        label='وضعیت',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    min_amount = forms.IntegerField(
        required=False,
        label='حداقل مبلغ',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'حداقل مبلغ به تومان'
        })
    )
    max_amount = forms.IntegerField(
        required=False,
        label='حداکثر مبلغ',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'حداکثر مبلغ به تومان'
        })
    )
    search = forms.CharField(
        required=False,
        label='جستجو',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'جستجو در کد پیگیری، نام کاربر و...'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        min_amount = cleaned_data.get('min_amount')
        max_amount = cleaned_data.get('max_amount')

        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError('تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد')

        if min_amount and max_amount and min_amount > max_amount:
            raise forms.ValidationError('حداقل مبلغ نمی‌تواند بیشتر از حداکثر مبلغ باشد')

        if date_to and date_to > timezone.now().date():
            raise forms.ValidationError('تاریخ پایان نمی‌تواند در آینده باشد')

        return cleaned_data

class SettlementBulkActionForm(forms.Form):
    settlement_ids = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    action = forms.ChoiceField(
        choices=[
            ('approve', 'تایید'),
            ('reject', 'رد'),
            ('cancel', 'لغو')
        ],
        required=True,
        widget=forms.RadioSelect
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'در صورت رد یا لغو، دلیل را وارد کنید'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        reason = cleaned_data.get('rejection_reason')

        if action in ['reject', 'cancel'] and not reason:
            raise forms.ValidationError('برای رد یا لغو درخواست، وارد کردن دلیل الزامی است')

        return cleaned_data

class SettlementReportForm(forms.Form):
    report_type = forms.ChoiceField(
        choices=[
            ('daily', 'روزانه'),
            ('weekly', 'هفتگی'),
            ('monthly', 'ماهانه')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    export_format = forms.ChoiceField(
        choices=[
            ('excel', 'Excel'),
            ('pdf', 'PDF'),
            ('csv', 'CSV')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
