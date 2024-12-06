from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.core.validators import RegexValidator
from .models import (
    SaleProperty, 
    RentProperty, 
    DailyRentProperty,
    PropertyImage, 
    Visit, 
    Booking
)

class SalePropertyForm(forms.ModelForm):
    class Meta:
        model = SaleProperty
        fields = [
            'title', 'description', 'property_type', 'district',
            'address', 'area', 'rooms', 'floor', 'total_floors',
            'parking', 'elevator', 'storage', 'balcony', 'package',
            'security', 'pool', 'gym', 'build_year', 'renovation',
            'document_type', 'direction', 'price', 'price_per_meter',
            'is_exchangeable', 'is_negotiable', 'exchange_description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'build_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'direction': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_meter': forms.NumberInput(attrs={'class': 'form-control'}),
            'exchange_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RentPropertyForm(forms.ModelForm):
    class Meta:
        model = RentProperty
        fields = [
            'title', 'description', 'property_type', 'district',
            'address', 'area', 'rooms', 'floor', 'total_floors',
            'parking', 'elevator', 'storage', 'balcony', 'package',
            'security', 'pool', 'gym', 'build_year', 'renovation',
            'document_type', 'direction', 'monthly_rent', 'deposit',
            'is_convertible', 'minimum_lease', 'has_transfer_fee'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'build_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'direction': forms.TextInput(attrs={'class': 'form-control'}),
            'monthly_rent': forms.NumberInput(attrs={'class': 'form-control'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_lease': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class DailyRentPropertyForm(forms.ModelForm):
    class Meta:
        model = DailyRentProperty
        fields = [
            'title', 'description', 'property_type', 'district',
            'address', 'area', 'rooms', 'floor', 'total_floors',
            'parking', 'elevator', 'storage', 'balcony', 'package',
            'security', 'pool', 'gym', 'build_year', 'renovation',
            'document_type', 'direction', 'daily_price', 'minimum_days',
            'maximum_days', 'capacity', 'extra_person_fee'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'daily_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'maximum_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'extra_person_fee': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'title', 'is_main', 'order']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PropertySearchForm(forms.Form):
    DEAL_CHOICES = (
        ('', 'نوع معامله'),
        ('sale', 'فروش'),
        ('rent', 'اجاره'),
        ('daily', 'اجاره روزانه'),
    )

    SORT_CHOICES = (
        ('', 'مرتب‌سازی'),
        ('price_low', 'قیمت: کم به زیاد'),
        ('price_high', 'قیمت: زیاد به کم'),
        ('area_low', 'متراژ: کم به زیاد'),
        ('area_high', 'متراژ: زیاد به کم'),
        ('date_new', 'جدیدترین'),
        ('date_old', 'قدیمی‌ترین'),
    )

    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'جستجو در عنوان، توضیحات و آدرس'
    }))
    
    deal_type = forms.ChoiceField(choices=DEAL_CHOICES, required=False, widget=forms.Select(attrs={
        'class': 'form-select'
    }))
    
    district = forms.ChoiceField(required=False, widget=forms.Select(attrs={
        'class': 'form-select'
    }))
    
    property_type = forms.ChoiceField(required=False, widget=forms.Select(attrs={
        'class': 'form-select'
    }))
    
    min_price = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'حداقل قیمت'
    }))
    
    max_price = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'حداکثر قیمت'
    }))
    
    min_area = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'حداقل متراژ'
    }))
    
    max_area = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'حداکثر متراژ'
    }))
    
    rooms = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'تعداد اتاق'
    }))
    
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, widget=forms.Select(attrs={
        'class': 'form-select'
    }))

class VisitRequestForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message="شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم باشد"
    )
    
    phone = forms.CharField(validators=[phone_regex], widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'شماره موبایل'
    }))

    class Meta:
        model = Visit
        fields = ['visitor', 'visit_date', 'visit_time', 'note']
        widgets = {
            'visit_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'visit_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'توضیحات اضافی'
            })
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'guests_count']
        widgets = {
            'check_in_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'check_out_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'guests_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out:
            if check_in >= check_out:
                raise forms.ValidationError('تاریخ ورود باید قبل از تاریخ خروج باشد')
            
            if check_in < timezone.now().date():
                raise forms.ValidationError('تاریخ ورود نمی‌تواند در گذشته باشد')
        
        return cleaned_data
