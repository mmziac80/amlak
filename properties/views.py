# -*- coding: utf-8 -*-
# Django imports

# Python Standard Library
import json
from decimal import Decimal
from typing import Any, Dict, cast

# Django Core
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser, User
from django.core.exceptions import ValidationError
from django.core.serializers import serialize
from django.db import models
from django.db.models import Q, QuerySet,F
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from itertools import chain

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
import requests

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView
)

# Third Party
import geopandas as gpd
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local Apps
from .models import (
    Property,
    PropertyImage,
    PropertyReview,
    SaleProperty,
    RentProperty,
    DailyRentProperty,
    Visit,
    Booking
)
from .serializers import (
    PropertySerializer,
    SalePropertySerializer,
    RentPropertySerializer,
    DailyRentPropertySerializer,
    PropertyImageSerializer,
    VisitSerializer,
    BookingSerializer
)
from .forms import (
    PropertySearchForm,
    VisitRequestForm,
    BookingForm,
    DailyRentPropertyForm,
    SalePropertyForm,
    RentPropertyForm
)
from .filters import (
    SalePropertyFilter,
    RentPropertyFilter,
    DailyRentPropertyFilter
)

import logging
logger = logging.getLogger(__name__)

User = get_user_model()

class HomeView(ListView):
    template_name = 'core/home.html'  # تمپلیت اصلی که شامل نقشه است

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        properties = Property.objects.filter(is_active=True)
        
        # تبدیل QuerySet به لیست دیکشنری‌ها
        properties_data = []
        for prop in properties:
            properties_data.append({
                'id': prop.pk,
                'title': prop.title,
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        float(prop.longitude) if prop.longitude else 0,
                        float(prop.latitude) if prop.latitude else 0
                    ]
                },
                'properties': {
                    'address': prop.address,
                    'price': prop.get_price_display(),
                    'type': prop.deal_type
                }
            })
        
        # ایجاد GeoDataFrame
        gdf = gpd.GeoDataFrame(properties_data)
        context['properties_json'] = gdf.to_json()
        
        return context

class PropertyListView(ListView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['properties'] = Property.objects.filter(is_active=True)
        return context



class PropertyDetailView(DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'

    def get_object(self, queryset: QuerySet | None = None) -> Property:
        obj = super().get_object(queryset)
        return cast(Property, obj) 
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        property_obj = self.get_object()
        map_settings = settings.MAP_WIDGETS['NeshanMap']

        # تعیین قیمت بر اساس نوع ملک
        if isinstance(property_obj, SaleProperty):
            price = property_obj.total_price
        elif isinstance(property_obj, RentProperty):
            price = property_obj.monthly_rent
        elif isinstance(property_obj, DailyRentProperty):
            price = property_obj.daily_price
        else:
            price = 0

        # اضافه کردن کلید API و تنظیمات نقشه به صورت مستقیم به زمینه
        context.update({
            'NESHAN_API_KEY': settings.NESHAN_API_KEY,
            'map_settings': map_settings,
            'initial_location': {
                'lat': float(property_obj.latitude) if property_obj.latitude is not None else map_settings['defaultCenter'][0],
                'lng': float(property_obj.longitude) if property_obj.longitude is not None else map_settings['defaultCenter'][1]
            },
            'nearby_places': self.get_nearby_places(property_obj),
            'property_info': {
                'title': property_obj.title,
                'price': str(price),
                'address': property_obj.address,
                'type': property_obj.deal_type
            }
        })

        if self.request.user.is_authenticated:
            user_id = self.request.user.pk
            context['is_favorite'] = property_obj.favorites.filter(pk=user_id).exists()

        return context


    def get_nearby_places(self, property_obj: Property) -> list[dict]:
        """Get nearby properties within a specific radius"""
        if not (property_obj.latitude and property_obj.longitude):
            return []

        nearby_properties = Property.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            is_active=True
        ).exclude(id=property_obj.id)

        result = []
        for prop in nearby_properties[:10]:
            # تعیین قیمت بر اساس نوع ملک
            if isinstance(prop, SaleProperty):
                price = prop.total_price
            elif isinstance(prop, RentProperty):
                price = prop.monthly_rent
            elif isinstance(prop, DailyRentProperty):
                price = prop.daily_price
            else:
                price = 0

            result.append({
                'id': prop.id,
                'title': prop.title,
                'lat': float(prop.latitude) if prop.latitude else 0.0,
                'lng': float(prop.longitude) if prop.longitude else 0.0,
                'type': prop.deal_type,
                'price': str(price) if price is not None else '0',
                'url': reverse('properties:detail', kwargs={'pk': prop.id})
            })

        return result

def reverse_geocode(lat, lng):
    url = f"https://api.neshan.org/v5/reverse?lat={lat}&lng={lng}"
    headers = {
        "Api-Key": "service.c3d3d02a266e4672843003b4c50f1eb9"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

class PropertyCreateView(LoginRequiredMixin, CreateView):
    model = Property
    template_name = 'properties/property_form.html'
    object = None  # تعریف صریح متغیر object
    fields = ['latitude', 'longitude', 'other_fields']  # Add other fields as necessary

    def get_form_class(self):
        property_type = self.request.GET.get('type', 'sale')
        if property_type == 'sale':
            return SalePropertyForm
        elif property_type == 'rent':
            return RentPropertyForm
        return DailyRentPropertyForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # تنظیمات پیش‌فرض برای موقعیت
        initial_location = {
            'lat': self.request.GET.get('lat', 36.2972),  # مختصات پیش‌فرض (مثلاً مشهد)
            'lng': self.request.GET.get('lng', 59.6067)
        }

        context.update({
            'map_center': initial_location,
            'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,  # کلید API گوگل
            'map_settings': {
                'zoom': 14,  # سطح زوم پیش‌فرض
            },
            'initial_location': json.dumps(initial_location)  # برای استفاده در JavaScript
        })
        return context
        
    def form_valid(self, form):
            print("=== DEBUG INFO ===")
            print("Form Data:", form.cleaned_data)
            print("Raw POST data:", self.request.POST)

            # Set owner and deal type
            form.instance.owner = self.request.user
            form.instance.deal_type = self.request.GET.get('type', 'sale')

            # Process coordinates with better error handling
            try:
                latitude = form.cleaned_data.get('latitude')
                longitude = form.cleaned_data.get('longitude')

                if latitude and longitude:
                    lat_float = float(latitude)
                    lng_float = float(longitude)

                    if self.is_valid_location(lat_float, lng_float):
                        form.instance.latitude = lat_float
                        form.instance.longitude = lng_float
                        form.instance.location = Point(lng_float, lat_float, srid=4326)
                        print(f"Location set successfully: {form.instance.location}")

                        # Reverse geocode to get the address
                        address_info = reverse_geocode(lat_float, lng_float)
                        if address_info:
                            formatted_address = address_info.get("formatted_address")
                            print("Formatted Address:", formatted_address)
                            # Optionally, save the formatted address to the form instance
                            form.instance.address = formatted_address

                    else:
                        raise ValueError("Invalid coordinates range")

            except Exception as e:
                print(f"Error processing location: {str(e)}")
                form.add_error(None, f'خطا در پردازش موقعیت مکانی: {str(e)}')
                return self.form_invalid(form)

            response = super().form_valid(form)
            print(f"Property saved successfully: ID={form.instance.id}")
            return response



    def is_valid_location(self, lat, lng):
        """اعتبارسنجی محدوده جغرافیایی"""
        return (
            -90 <= lat <= 90 and
            -180 <= lng <= 180
        )

    def get_success_url(self):
        property_type = self.request.GET.get('type', 'sale')
        urls = {
            'sale': 'properties:sale_properties',
            'rent': 'properties:rent_properties',
            'daily': 'properties:daily_list'
        }
        return reverse_lazy(urls.get(property_type, 'properties:sale_properties'))


class PropertyUpdateView(LoginRequiredMixin, UpdateView):
    model = Property
    template_name = 'properties/property_form.html'
    

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        property_obj = cast(Property, self.get_object())

        # تنظیمات نقشه گوگل
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        context['map_settings'] = {
            'center': {
                'lat': property_obj.latitude or 36.2972,  # مختصات پیش‌فرض (مثلاً مشهد)
                'lng': property_obj.longitude or 59.6067
            },
            'zoom': 14,  # سطح زوم پیش‌فرض
        }
        return context
        
       

    def form_valid(self, form):
        print("=== UPDATE DEBUG INFO ===")
        print("Form Data:", form.cleaned_data)
        
        try:
            lat = form.cleaned_data.get('latitude')
            lng = form.cleaned_data.get('longitude')
            
            if lat and lng:
                lat_float = float(lat)
                lng_float = float(lng)
                
                # اعتبارسنجی مختصات
                if -90 <= lat_float <= 90 and -180 <= lng_float <= 180:
                    form.instance.latitude = lat_float
                    form.instance.longitude = lng_float
                    form.instance.location = Point(lng_float, lat_float, srid=4326)
                    print(f"Location updated: {form.instance.location}")
                else:
                    raise ValueError("Invalid coordinates range")
                    
        except Exception as e:
            print(f"Error updating location: {str(e)}")
            form.add_error(None, f'خطا در به‌روزرسانی موقعیت مکانی: {str(e)}')
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        print(f"Property updated successfully: ID={form.instance.id}")
        return response



class PropertyDeleteView(LoginRequiredMixin, DeleteView):
    model = Property
    success_url = reverse_lazy('properties:list')
    template_name = 'properties/property_confirm_delete.html'

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

class PropertySearchView(ListView):
    template_name = 'properties/map_filter.html'
    context_object_name = 'properties'
    paginate_by = 12

    def get_queryset(self):
        # تعریف پارامترهای جستجو با اعتبارسنجی
        query = self.request.GET.get('q', '').strip()
        property_type = self.request.GET.get('type', 'all')
        
        # تبدیل و اعتبارسنجی مختصات
        try:
            lat = float(self.request.GET.get('lat', 0))
            lng = float(self.request.GET.get('lng', 0))
            radius = float(self.request.GET.get('radius', 5000))
            has_location = bool(lat and lng)
        except (ValueError, TypeError):
            has_location = False
            lat = lng = radius = 0

        # ساخت فیلترهای پایه
        filters = Q()
        if query:
            filters = Q(title__icontains=query) | \
                    Q(description__icontains=query) | \
                    Q(address__icontains=query)

        # اضافه کردن فیلتر مکانی
        if has_location:
            point = Point(lng, lat, srid=4326)
            filters &= Q(location__distance_lte=(point, D(m=radius)))

        # دریافت نتایج بر اساس نوع ملک
        MODEL_MAP = {
            'sale': SaleProperty,
            'rent': RentProperty,
            'daily': DailyRentProperty
        }

        if property_type in MODEL_MAP:
            queryset = MODEL_MAP[property_type].objects.filter(filters)
        else:
            queryset = list(chain(*[
                model.objects.filter(filters)
                for model in MODEL_MAP.values()
            ]))

        # مرتب‌سازی بر اساس فاصله
        if has_location:
            if isinstance(queryset, list):
                point_obj = Point(lng, lat, srid=4326)
                queryset.sort(key=lambda x: 
                    x.location.distance(point_obj) if x.location else float('inf'))
            else:
                queryset = queryset.annotate(
                    distance=Distance('location', point)
                ).order_by('distance')

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_params'] = self.request.GET.dict()
        return context


class AdvancedSearchView(ListView):
    template_name = 'properties/advanced_search.html'
    context_object_name = 'properties'
    paginate_by = 12

    def get_queryset(self):
        filters = self.request.GET
        queryset = Property.objects.filter(is_active=True)

        # فیلترهای قیمت با اعتبارسنجی
        try:
            if price_min := filters.get('price_min'):
                price_min = float(price_min)
                queryset = queryset.filter(
                    Q(saleproperty__total_price__gte=price_min) |
                    Q(rentproperty__monthly_rent__gte=price_min) |
                    Q(dailyrentproperty__daily_price__gte=price_min)
                )
        except ValueError:
            pass

        # فیلتر موقعیت مکانی
        if location := filters.get('location'):
            try:
                lat, lng = map(float, location.split(','))
                radius = float(filters.get('radius', 5))
                point = Point(lng, lat, srid=4326)
                queryset = queryset.filter(
                    location__distance_lte=(point, D(km=radius))
                )
            except (ValueError, TypeError):
                pass

        # فیلترهای اضافی
        for field in ['property_type', 'district']:
            if value := filters.get(field):
                queryset = queryset.filter(**{field: value})

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_filters'] = self.request.GET
        return context

class PropertyLocationFilter(TemplateView):
    template_name = 'properties/map_filter.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # اضافه کردن کلید API نشان به context
        context.update({
            'NESHAN_API_KEY': settings.NESHAN_API_KEY,
            'map_settings': settings.MAP_WIDGETS['NeshanMap'],
            'initial_location': {
                'lat': self.request.GET.get('lat', 35.6892),
                'lng': self.request.GET.get('lng', 51.3890)
            }
        })
        return context
    

# اضافه کردن view های جدید
class SalePropertyListView(ListView):
    model = SaleProperty
    template_name = 'properties/sale_property_list.html'
    context_object_name = 'properties'
    paginate_by = 12
class SalePropertySearchView(ListView):
    model = SaleProperty
    template_name = 'properties/sale_search.html'
    context_object_name = 'properties'
    paginate_by = 12
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['properties'] = SaleProperty.objects.filter(is_active=True)
            return context
    
class SalePropertyDetailView(PropertyDetailView):  # ارث‌بری از PropertyDetailView
    template_name = 'properties/property_detail.html'

    def get_queryset(self):
        # فیلتر کردن فقط املاک فروشی
        return Property.objects.filter(deal_type='sale')

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        property_obj = self.get_object()

        # اضافه کردن یا تغییر منطق خاص برای املاک فروشی
        if self.request.user.is_authenticated:
            context['is_favorite'] = property_obj.favorites.filter(
                pk=self.request.user.pk
            ).exists()

        return context


class RentPropertyListView(ListView):
    model = RentProperty
    template_name = 'properties/rent_property_list.html'
    context_object_name = 'properties'
    paginate_by = 12
class RentPropertySearchView(ListView):
    model = RentProperty
    template_name = 'properties/rent_search.html'
    context_object_name = 'properties'
    paginate_by = 12

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['properties'] = RentProperty.objects.filter(is_active=True)
            return context
    
class RentPropertyDetailView(PropertyDetailView):  # ارث‌بری از PropertyDetailView
    template_name = 'properties/property_detail.html'  # استفاده از قالب یکپارچه

    def get_queryset(self):
        # فیلتر کردن فقط املاک اجاره‌ای
        return Property.objects.filter(deal_type='rent')

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        property_obj = self.get_object()

        # اضافه کردن یا تغییر منطق خاص برای املاک اجاره‌ای
        if self.request.user.is_authenticated:
            context['is_favorite'] = property_obj.favorites.filter(
                pk=self.request.user.pk
            ).exists()

        return context

import logging
logger = logging.getLogger(__name__)











class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [IsAuthenticated]

class VisitViewSet(viewsets.ModelViewSet):
    serializer_class = VisitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self) -> QuerySet:
        # تبدیل نوع کاربر به AbstractUser
        user = cast(AbstractUser, self.request.user)
        
        # حالا می‌توانیم مستقیماً به is_staff دسترسی داشته باشیم
        if user.is_staff:
            return Visit.objects.all()
        return Visit.objects.filter(visitor=user)

    def perform_create(self, serializer):
        serializer.save(visitor=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        User = get_user_model()
        # تبدیل نوع با cast برای اطمینان از دسترسی به is_staff
        user = cast(AbstractUser, self.request.user)

        if user.is_staff:  # حالا Pylance می‌داند user دارای is_staff است
            return Visit.objects.all()
        return Visit.objects.filter(visitor=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteListView(LoginRequiredMixin, ListView):
    template_name = 'properties/favorites.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        user = self.request.user
        return {
            'sale': SaleProperty.objects.filter(favorites=user),
            'rent': RentProperty.objects.filter(favorites=user),
            'daily': DailyRentProperty.objects.filter(favorites=user)
        }
class DailyRentPropertyListView(ListView):
    model = DailyRentProperty
    template_name = 'properties/daily_property_list.html'
    context_object_name = 'properties'
    paginate_by = 12


class DailyRentPropertySearchView(ListView):
    model = DailyRentProperty
    template_name = 'properties/daily_property_search.html'
    context_object_name = 'properties'
    
    def get_queryset(self):
        queryset = DailyRentProperty.objects.all()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(title__icontains=q)
        return queryset
    
class DailyRentPropertyDetailView(DetailView):
    model = DailyRentProperty
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'
    favorites = models.ManyToManyField(User, related_name='favorite_properties', blank=True)


    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        logger.info(f"Retrieved DailyRentProperty object: {obj.pk}")  # استفاده از pk
        return obj


    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            property_obj = cast(DailyRentProperty, self.get_object())

            # علاقه‌مندی‌ها
            if self.request.user.is_authenticated:
                context['is_favorite'] = property_obj.favorites.filter(
                    pk=self.request.user.pk  # تغییر id به pk
                ).exists()

            # اطلاعات رزروها
            bookings = property_obj.bookings.filter(status='confirmed')
            context['bookings'] = bookings

            # تاریخ‌های رزرو شده
            context['booked_dates'] = [
                {
                    'start': booking.check_in_date,
                    'end': booking.check_out_date
                } for booking in bookings
            ]

            # فرم و محاسبات
            context.update({
                'booking_form': BookingForm(),
                'daily_price': property_obj.daily_price,
                'extra_person_fee': property_obj.extra_person_fee,
                'min_stay': property_obj.min_stay,
                'max_guests': property_obj.max_guests
            })

            logger.info(f"Context prepared successfully for property {property_obj.id}")
            return context

        except Exception as e:
            logger.error(f"Error in get_context_data: {str(e)}")
            raise

class DailyRentPropertyAdvancedSearchView(ListView):
    model = DailyRentProperty
    template_name = 'properties/daily_rent_search.html'
    context_object_name = 'properties'
    paginate_by = 12

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        properties = DailyRentProperty.objects.filter(is_active=True)
        print(f"Found {properties.count()} properties") # برای دیباگ
        context['properties'] = properties
        return context
    
   

class DailyRentPropertyBookView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'properties/booking_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.property = get_object_or_404(DailyRentProperty, pk=self.kwargs['pk'])
        return super().form_valid(form)

class DailyRentPropertyPaymentView(LoginRequiredMixin, UpdateView):
    model = Booking
    fields = []
    template_name = 'properties/payment_form.html'
    
    def get_success_url(self) -> str:
        booking_obj = cast(Booking, self.get_object())
        return reverse('properties:daily_detail', kwargs={'pk': booking_obj.property.pk})

class DailyRentPropertyCreateView(LoginRequiredMixin, CreateView):
    model = DailyRentProperty
    form_class = DailyRentPropertyForm
    template_name = 'properties/daily_property_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # تنظیمات نقشه نشان
        map_settings = settings.MAP_WIDGETS['NeshanMap']
        context['map_center'] = {
            'lat': map_settings['defaultCenter'][0],
            'lng': map_settings['defaultCenter'][1]
        }
        context['NESHAN_API_KEY'] = settings.NESHAN_API_KEY
        context['map_settings'] = {
            'zoom': map_settings['zoom'],
            'mapStyle': map_settings['mapStyle'],
            'poi': map_settings['poi'],
            'traffic': map_settings['traffic']
        }
        return context

    def form_valid(self, form):
        # تنظیم مالک
        form.instance.owner = self.request.user
        # تنظیم نوع معامله به اجاره روزانه
        form.instance.deal_type = 'daily'
        
        # پردازش اطلاعات موقعیت مکانی
        if form.cleaned_data.get('location'):
            location_data = json.loads(form.cleaned_data['location'])
            form.instance.latitude = location_data['lat']
            form.instance.longitude = location_data['lng']
            
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('properties:daily_list')
    
class DailyRentPropertyUpdateView(LoginRequiredMixin, UpdateView):
    model = DailyRentProperty
    form_class = DailyRentPropertyForm
    template_name = 'properties/daily_property_form.html'

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        property_obj = cast(DailyRentProperty, self.get_object())
        
        # Get Neshan map settings from Django settings
        map_settings = settings.MAP_WIDGETS['NeshanMap']
        
        context.update({
            'NESHAN_API_KEY': settings.NESHAN_API_KEY,
            'map_settings': {
                'center': {
                    'lat': float(property_obj.latitude) if property_obj.latitude else map_settings['defaultCenter'][0],
                    'lng': float(property_obj.longitude) if property_obj.longitude else map_settings['defaultCenter'][1]
                },
                'zoom': map_settings['zoom'],
                'mapStyle': map_settings['mapStyle'],
                'poi': map_settings['poi'],
                'traffic': map_settings['traffic']
            }
        })
        
        return context
    
class DailyRentPropertyDeleteView(LoginRequiredMixin, DeleteView):
    model = DailyRentProperty
    template_name = 'properties/daily_property_confirm_delete.html'
    success_url = reverse_lazy('properties:daily_list')


# بعد از DailyRentPropertyDeleteView اضافه کنید
class DailyRentBookingView(LoginRequiredMixin, CreateView):
    model = Booking
    template_name = 'properties/daily/booking.html'
    fields = ['check_in_date', 'check_out_date', 'guests_count']
    object = None  # تعریف صریح متغیر object
    
    def form_valid(self, form):
        form.instance.property = get_object_or_404(DailyRentProperty, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        
        if form.instance.property.is_available(
            form.instance.check_in_date,
            form.instance.check_out_date
        ):
            result = super().form_valid(form)
            self.object = form.instance  # ذخیره شیء ایجاد شده
            messages.success(self.request, 'رزرو با موفقیت ثبت شد')
            return result
        
        messages.error(self.request, 'این تاریخ قبلاً رزرو شده است')
        return self.form_invalid(form)
    
    def get_success_url(self) -> str:
        if not self.object or not self.object.id:
            raise ValueError("شناسه رزرو نامعتبر است")
            
        return reverse('payments:create', kwargs={'booking_id': self.object.id})

class DailyRentCalendarView(DetailView):
    model = DailyRentProperty
    template_name = 'properties/daily/calendar.html'
    context_object_name = 'property'
    
    def get_object(self, queryset: QuerySet | None = None) -> DailyRentProperty:
        obj = super().get_object(queryset)
        return cast(DailyRentProperty, obj)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property_obj = cast(DailyRentProperty, self.get_object())
        bookings = property_obj.bookings.filter(status='confirmed')
        
        context['bookings_json'] = [{
            'title': 'رزرو شده',
            'start': booking.check_in_date,
            'end': booking.check_out_date,
            'color': '#ff4444'
        } for booking in bookings]
        
        return context

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'properties/booking_form.html'

    def form_valid(self, form):
        property_obj = get_object_or_404(DailyRentProperty, pk=self.kwargs['pk'])
        form.instance.property = property_obj
        form.instance.user = self.request.user
        form.instance.total_price = property_obj.calculate_price(
            form.cleaned_data['check_in_date'],
            form.cleaned_data['check_out_date']
        )
        return super().form_valid(form)

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'properties/booking_detail.htmll'
    context_object_name = 'booking'

class VisitRequestView(LoginRequiredMixin, CreateView):
    model = Visit
    form_class = VisitRequestForm
    template_name = 'properties/visit_form.html'

    def get_success_url(self):
        # برگشت به صفحه جزئیات ملک
        property_type = self.kwargs['type']  # نوع ملک (rent/sale/daily)
        if property_type == 'rent':
            return reverse('properties:rent_detail', kwargs={'pk': self.kwargs['pk']})
        elif property_type == 'sale':
            return reverse('properties:sale_detail', kwargs={'pk': self.kwargs['pk']})
        else:
            return reverse('properties:daily_detail', kwargs={'pk': self.kwargs['pk']})
    def form_valid(self, form):
        # تنظیم کاربر و ملک
        form.instance.visitor = self.request.user
        form.instance.property = get_object_or_404(
            self.get_property_model(),
            pk=self.kwargs['pk']
        )

        # تاریخ بازدید از قبل در clean_visit_date تبدیل شده است
        # نیازی به تبدیل مجدد نیست
        form.instance.visit_date = form.cleaned_data['visit_date']

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'درخواست بازدید با موفقیت ثبت شد'
            })

        messages.success(self.request, 'درخواست بازدید شما با موفقیت ثبت شد')
        return super().form_valid(form)


    def get_property_model(self):
        property_type = self.kwargs.get('type')
        if property_type == 'sale':
            return SaleProperty
        elif property_type == 'rent':
            return RentProperty
        return DailyRentProperty


class PropertyReviewView(LoginRequiredMixin, CreateView):
    model = PropertyReview
    fields = ['rating', 'comment']
    template_name = 'properties/review_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.property_id = self.kwargs['pk']
        messages.success(self.request, 'نظر شما با موفقیت ثبت شد')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('properties:detail', kwargs={'pk': self.kwargs['pk']})

class PropertyFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # جستجو در هر سه نوع ملک
        property_obj = None
        for model in [SaleProperty, RentProperty, DailyRentProperty]:
            try:
                property_obj = model.objects.get(pk=pk)
                break
            except model.DoesNotExist:
                continue
                
        if not property_obj:
            raise Http404("ملک مورد نظر یافت نشد")
            
        # اضافه یا حذف کردن از علاقه‌مندی‌ها
        if request.user in property_obj.favorites.all():
            property_obj.favorites.remove(request.user)
            is_favorite = False
            message = 'ملک از علاقه‌مندی‌ها حذف شد'
        else:
            property_obj.favorites.add(request.user)
            is_favorite = True
            message = 'ملک به علاقه‌مندی‌ها اضافه شد'
            
        # پاسخ به درخواست AJAX
        if request.is_ajax():
            return JsonResponse({
                'status': 'success',
                'is_favorite': is_favorite,
                'message': message
            })
        
        # پاسخ به درخواست معمولی
        messages.success(request, message)
        return redirect('properties:detail', pk=pk)

class PropertyImageUploadView(CreateView):
    model = PropertyImage
    fields = ['image', 'title', 'is_main', 'order']
    template_name = 'properties/property_image_upload.html'

    def form_valid(self, form):
        # دریافت property از پارامترهای URL
        property_obj = get_object_or_404(Property, pk=self.kwargs['pk'])
        form.instance.property = property_obj
        return super().form_valid(form)
    
class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class SalePropertyViewSet(viewsets.ModelViewSet):
    queryset = SaleProperty.objects.all()
    serializer_class = SalePropertySerializer
    filterset_class = SalePropertyFilter
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class RentPropertyViewSet(viewsets.ModelViewSet):
    queryset = RentProperty.objects.all()
    serializer_class = RentPropertySerializer
    filterset_class = RentPropertyFilter
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class DailyRentPropertyViewSet(viewsets.ModelViewSet):
    queryset = DailyRentProperty.objects.all()
    serializer_class = DailyRentPropertySerializer
    filterset_class = DailyRentPropertyFilter
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BookingDetailAPIView(APIView):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

# این ویو را هم اضافه کنید        
class CheckAvailabilityView(APIView):
    def get(self, request, property_id):
        property = get_object_or_404(Property, id=property_id)
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        
        is_available = property.check_availability(check_in, check_out)
        return Response({
            'is_available': is_available
        })
    
def safe_float(value):
    if value is None:
        return 0.0
    return float(value)

class PropertyPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    property.increment_views()  # افزایش بازدید
    popularity = property.get_popularity_score()  # محاسبه محبوبیت
    
    context = {
        'property': property,
        'popularity': popularity,
        'features': property.get_features_display(),
        'full_address': property.get_full_address()
    }
    
    return render(request, 'properties/property_detail.html', context)
    
@api_view(['GET'])
def nearby_properties_api(request):
    try:
        logger.debug(f"Received filters: {request.GET}")

        # Validate and get location parameters with defaults
        lat = float(request.GET.get('lat', 35.6892))
        lng = float(request.GET.get('lng', 51.3890))
        radius = int(request.GET.get('radius', 5))
        logger.debug(f"Location params: lat={lat}, lng={lng}, radius={radius}")

        # Get filter parameters with type validation
        filters = {
            'property_type': request.GET.get('propertyType'),
            'min_price': request.GET.get('minPrice'),
            'max_price': request.GET.get('maxPrice'),
            'min_area': request.GET.get('minArea'),
            'max_area': request.GET.get('maxArea'),
            'has_parking': request.GET.get('parking') == 'true',
            'has_elevator': request.GET.get('elevator') == 'true'
        }
        logger.debug(f"Applied filters: {filters}")

        # Build query
        queryset = Property.get_properties_within_radius(lat, lng, radius)
        logger.debug(f"Initial queryset count: {queryset.count()}")

        
        # Apply filters dynamically
        filter_conditions = Q()

        # فیلتر نوع ملک
        if filters['property_type']:
            filter_conditions &= Q(deal_type=filters['property_type'])

        # فیلتر قیمت بر اساس نوع ملک
        if filters['min_price'] or filters['max_price']:
            min_price = float(filters['min_price']) if filters['min_price'] else 0
            max_price = float(filters['max_price']) if filters['max_price'] else float('inf')
            
            price_conditions = Q()
            if filters['property_type'] == 'sale':
                # برای املاک فروشی از total_price استفاده می‌کنیم
                price_conditions = Q(
                    saleproperty__total_price__gte=min_price,
                    saleproperty__total_price__lte=max_price
                )
            elif filters['property_type'] == 'rent':
                # برای املاک اجاره‌ای از monthly_rent استفاده می‌کنیم
                price_conditions = Q(
                    rentproperty__monthly_rent__gte=min_price,
                    rentproperty__monthly_rent__lte=max_price
                )
            elif filters['property_type'] == 'daily':
                # برای املاک روزانه از daily_price استفاده می‌کنیم
                price_conditions = Q(
                    dailyrentproperty__daily_price__gte=min_price,
                    dailyrentproperty__daily_price__lte=max_price
                )
            
            filter_conditions &= price_conditions

        # فیلتر مساحت
        if filters['min_area']:
            filter_conditions &= Q(area__gte=float(filters['min_area']))
        if filters['max_area']:
            filter_conditions &= Q(area__lte=float(filters['max_area']))
            
        if filters['has_parking']:
            filter_conditions &= Q(parking=True)
        if filters['has_elevator']:
            filter_conditions &= Q(elevator=True)

        # Apply filters to queryset
        queryset = queryset.filter(filter_conditions)
        logger.debug(f"Final queryset count: {queryset.count()}")

        # Handle empty results early
        if not queryset.exists():
            return Response({
                'count': 0,
                'next': None,
                'previous': None,
                'results': []
            })

        # Apply pagination
        paginator = PropertyPagination()
        page = paginator.paginate_queryset(queryset, request)

        # Transform to JSON response
        results = [{
            'id': prop.id,
            'title': prop.title,
            'price': {
                'sale': prop.saleproperty.total_price if hasattr(prop, 'saleproperty') else None,
                'rent': {
                    'monthly': prop.rentproperty.monthly_rent if hasattr(prop, 'rentproperty') else None,
                    'deposit': prop.rentproperty.deposit if hasattr(prop, 'rentproperty') else None
                },
                'daily': prop.dailyrentproperty.daily_price if hasattr(prop, 'dailyrentproperty') else None,
                'display': prop.get_price_display()
            },
            'area': safe_float(prop.area),
            'address': prop.address,
            'location': {
                'lat': safe_float(prop.latitude),
                'lng': safe_float(prop.longitude)
            },
            'type': prop.deal_type,
            'features': {
                'parking': bool(prop.parking),
                'elevator': bool(prop.elevator)
            },
            'url': prop.get_absolute_url()
        } for prop in page] if page else []


        return paginator.get_paginated_response(results)

    except ValueError as e:
        return Response({'error': f'Invalid parameter value: {str(e)}'}, status=400)
    except ValidationError as e:
        return Response({'error': f'Validation error: {str(e)}'}, status=400)
    except Exception as e:
        logger.error(f"Error in nearby_properties_api: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)
    
def property_locations_api(request):
    properties = Property.objects.all()
    print("تعداد املاک:", properties.count())
    print("املاک با موقعیت:", properties.filter(latitude__isnull=False).count())
    data = [prop.to_map_data() for prop in properties.filter(latitude__isnull=False)]
    return JsonResponse(data, safe=False)








