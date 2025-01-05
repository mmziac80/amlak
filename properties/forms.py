# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django import forms
import geopandas as gpd
from django.forms.widgets import TextInput
from datetime import datetime, date

from django.forms import widgets

from django.core.validators import RegexValidator
from persiantools.jdatetime import JalaliDate

from .models import (

    SaleProperty, 
    RentProperty, 
    DailyRentProperty,
    PropertyImage, 
    Visit, 
    Booking
)

class SalePropertyForm(forms.ModelForm):
    # Hidden fields for map coordinates
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    location = forms.CharField(widget=forms.HiddenInput(), required=False)


    class Meta:
        model = SaleProperty
        fields = [
            # Main Info
            'title', 'description', 'property_type',
            
            # Location
            'district', 'address', 'latitude', 'longitude',
            
            # Property Details
            'area', 'rooms', 'floor', 'total_floors', 'build_year',
            
            # Amenities
            'parking', 'elevator', 'storage', 'balcony', 'package',
            'security', 'pool', 'gym', 'renovation',
            
            # Price and Terms
            'total_price', 'price_per_meter', 'is_exchangeable',
            'is_negotiable', 'exchange_description'
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
            'total_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_meter': forms.NumberInput(attrs={'class': 'form-control'}),
            'exchange_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'elevator': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'storage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'balcony': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'package': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'security': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pool': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gym': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'renovation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_exchangeable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.deal_type = 'sale'
    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('latitude')
        lng = cleaned_data.get('longitude')
        
        if lat and lng:
            if not (-90 <= float(lat) <= 90) or not (-180 <= float(lng) <= 180):
                raise forms.ValidationError('مختصات جغرافیایی نامعتبر است')
        
        return cleaned_data

class RentPropertyForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = RentProperty
        fields = [
            # Main Info
            'title', 'description', 'property_type',
            
            # Location
            'district', 'address', 'latitude', 'longitude',
            
            # Property Details
            'area', 'rooms', 'floor', 'total_floors', 'build_year',
            
            # Amenities
            'parking', 'elevator', 'storage', 'balcony', 'package',
            'security', 'pool', 'gym', 'renovation',
            
            # Rental Terms
            'monthly_rent', 'deposit', 'is_convertible',
            'minimum_lease', 'has_transfer_fee'
        ]

        widgets = {
            # Text inputs
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # Select inputs
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            
            # Number inputs
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'build_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'monthly_rent': forms.NumberInput(attrs={'class': 'form-control'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_lease': forms.NumberInput(attrs={'class': 'form-control'}),
            
            # Checkbox inputs
            'parking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'elevator': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'storage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'balcony': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'package': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'security': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pool': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gym': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'renovation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_convertible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_transfer_fee': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.deal_type = 'rent'


class DailyRentPropertyForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = DailyRentProperty
        fields = [
            # Main Info
            'title', 'description', 'property_type',
            
            # Location
            'district', 'address', 'latitude', 'longitude',
            
            # Property Details
            'area', 'rooms', 'floor', 'total_floors', 'build_year',
            
            # Amenities
            'parking', 'elevator', 'storage', 'balcony', 'package',
            'security', 'pool', 'gym', 'renovation',
            
            # Stay Conditions
            'daily_price', 'min_stay', 'maximum_days', 'max_guests',
            'extra_person_fee', 'check_in_time', 'check_out_time'
        ]

        widgets = {
            # Text inputs
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # Select inputs
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            
            # Number inputs
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'build_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'daily_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_stay': forms.NumberInput(attrs={'class': 'form-control'}),
            'maximum_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_guests': forms.NumberInput(attrs={'class': 'form-control'}),
            'extra_person_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            
            # Time inputs
            'check_in_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'check_out_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            
            # Checkbox inputs
            'parking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'elevator': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'storage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'balcony': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'package': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'security': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pool': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gym': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'renovation': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.deal_type = 'daily'


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

from jdatetime import datetime as jdatetime
from django import forms
from django.core.validators import RegexValidator
from .models import Visit
class VisitRequestForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message="شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم باشد"
    )
    
    phone = forms.CharField(
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control glass-input',
            'placeholder': 'شماره موبایل'
        })
    )

    visit_date = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control glass-input datepicker',
            'readonly': 'readonly',
            'data-toggle': 'datepicker',
            'autocomplete': 'off',
            'placeholder': 'تاریخ بازدید را انتخاب کنید'
        })
    )

    class Meta:
        model = Visit
        fields = ['visitor', 'visit_date', 'visit_time', 'notes']
        widgets = {
            'visit_time': forms.TimeInput(attrs={
                'class': 'form-control glass-input',
                'type': 'time',
                'min': '09:00',
                'max': '20:00'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control glass-input',
                'rows': 3,
                'placeholder': 'توضیحات خود را وارد کنید',
                'autocomplete': 'off'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['visit_date'].label = 'تاریخ بازدید'
        self.fields['visit_time'].label = 'ساعت بازدید'
        self.fields['notes'].label = 'توضیحات'

    def clean_visit_date(self):
        date_str = self.cleaned_data['visit_date']
        print(f"Received date string: {date_str}")

        try:
            # تجزیه رشته تاریخ
            year, month, day = map(int, date_str.split('/'))
            print(f"Parsed date components: year={year}, month={month}, day={day}")
            
            # ساخت تاریخ جلالی
            jalali_date = jdatetime(year, month, day).date()
            print(f"Created Jalali date: {jalali_date}")
            
            # تبدیل به تاریخ میلادی
            gregorian_date = jalali_date.togregorian()
            print(f"Converted to Gregorian: {gregorian_date}")
            
            # بررسی تاریخ گذشته
            if gregorian_date < date.today():
                raise forms.ValidationError('تاریخ بازدید نمی‌تواند در گذشته باشد')
            
            return gregorian_date

        except ValueError as e:
            print(f"Error converting date: {str(e)}")
            raise forms.ValidationError('فرمت تاریخ نامعتبر است')

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
            # بررسی ترتیب تاریخ‌ها
            if check_in >= check_out:
                raise forms.ValidationError('تاریخ ورود باید قبل از تاریخ خروج باشد')
            
            # بررسی تاریخ گذشته
            if check_in < timezone.now().date():
                raise forms.ValidationError('تاریخ ورود نمی‌تواند در گذشته باشد')
                
            # محاسبه تعداد شب‌های اقامت
            nights = (check_out - check_in).days
            
            # دریافت حداقل مدت اقامت از property
            property_obj = self.instance.property
            if nights < property_obj.min_stay:
                raise forms.ValidationError(
                    f'حداقل مدت اقامت {property_obj.min_stay} شب است. '
                    f'شما {nights} شب را انتخاب کرده‌اید.'
                )
        
        return cleaned_data




