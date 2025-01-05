# -*- coding: utf-8 -*-

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='list'),
    path('create/', views.PaymentInitiateView.as_view(), name='create'),
    path('verify/', views.PaymentVerifyView.as_view(), name='verify'),
    path('history/', views.PaymentHistoryView.as_view(), name='history'),
    path('callback/', views.PaymentCallbackView.as_view(), name='callback'),
]



