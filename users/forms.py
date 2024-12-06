from django import forms
from django.core.validators import MinValueValidator
from .models import Property, PropertyImage, Visit

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 
            'property_type', 
            'district', 
            'address',
            'price', 
            'area', 
            'rooms', 
            'floor', 
            'total_floors',
            'parking', 
            'elevator', 
            'storage', 
            'balcony',
            'description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان ملک'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'آدرس کامل'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'قیمت به تومان'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'متراژ به متر مربع'}),
            'rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'توضیحات تکمیلی'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise forms.ValidationError('قیمت نمی‌تواند منفی باشد')
        return price

    def clean_area(self):
        area = self.cleaned_data.get('area')
        if area and area < 0:
            raise forms.ValidationError('متراژ نمی‌تواند منفی باشد')
        return area

class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class PropertySearchForm(forms.Form):
    PRICE_RANGES = [
        ('', 'همه محدوده‌های قیمتی'),
        ('0-500', 'تا ۵۰۰ میلیون تومان'),
        ('500-1000', '۵۰۰ تا ۱۰۰۰ میلیون تومان'),
        ('1000-2000', '۱ تا ۲ میلیارد تومان'),
        ('2000+', 'بالای ۲ میلیارد تومان')
    ]

    AREA_RANGES = [
        ('', 'همه متراژها'),
        ('0-50', 'تا ۵۰ متر'),
        ('50-100', '۵۰ تا ۱۰۰ متر'),
        ('100-200', '۱۰۰ تا ۲۰۰ متر'),
        ('200+', 'بالای ۲۰۰ متر')
    ]

    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'جستجو در عنوان و توضیحات'})
    )
    property_type = forms.ChoiceField(
        choices=[('', 'همه انواع ملک')] + Property.PROPERTY_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    district = forms.ChoiceField(
        choices=[('', 'همه مناطق')] + Property.DISTRICTS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    price_range = forms.ChoiceField(
        choices=PRICE_RANGES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    area_range = forms.ChoiceField(
        choices=AREA_RANGES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    rooms = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'تعداد اتاق'})
    )
    parking = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    elevator = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    storage = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class VisitRequestForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['preferred_date', 'preferred_time', 'description']
        widgets = {
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'preferred_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'توضیحات اضافی'
            })
        }
