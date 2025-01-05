# -*- coding: utf-8 -*-


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views
app_name = 'users'

urlpatterns = [
    # احراز هویت
    path('login/', views.PhoneLoginView.as_view(), name='phone-login'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('logout/', views.logout_view, name='logout'),

    # پروفایل
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile-edit'),
    path('profile/verify/', views.verify_identity, name='verify-identity'),

    # اعلان‌ها
    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/<int:pk>/read/', views.notification_read, name='notification-read'),

    # API endpoints
    path('api/register/', views.register_api, name='api-register'),
    path('api/verify-otp/', views.verify_otp_api, name='api-verify-otp'),
] 
# Media and Static Files URLs
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom Error Pages
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'

# Admin Site Customization
admin.site.site_header = 'مدیریت سامانه املاک'
admin.site.site_title = 'پنل مدیریت'
admin.site.index_title = 'مدیریت سامانه'

