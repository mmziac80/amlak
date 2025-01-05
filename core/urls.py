# -*- coding: utf-8 -*-

from django.urls import path
from . import views
from .views import property_locations_api


app_name = 'core'

urlpatterns = [
    # صفحه اصلی
    path('', views.HomeView.as_view(), name='home'),
    
    # ثبت نام و داشبورد
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # صفحات استاتیک
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    
    # جستجو و آمار
    path('search/', views.SearchView.as_view(), name='search'),
    path('stats/', views.StatsView.as_view(), name='stats'),
    path('api/properties/', property_locations_api, name='property_locations_api'),

]
