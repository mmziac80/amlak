# -*- coding: utf-8 -*-


# properties/api/urls.py
from django.urls import path
from properties import views

app_name = 'properties_api'

urlpatterns = [
    # API رزرو
    path('bookings/create/', 
         views.BookingCreateView.as_view(),
         name='booking_create'),
    
    path('bookings/<int:booking_id>/',
         views.BookingDetailView.as_view(), 
         name='booking_detail'),
    
    # API بررسی موجود بودن
    path('properties/<int:property_id>/check-availability/',
         views.CheckAvailabilityView.as_view(), 
         name='check_availability'),
]

