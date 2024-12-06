from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # ثبت نام و پروفایل
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    
    # مدیریت رمز عبور
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='users/password_change.html',
        success_url='/users/password-change/done/'
    ), name='password_change'),
    
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='users/password_change_done.html'
    ), name='password_change_done'),

    # علاقه‌مندی‌ها و املاک من
    path('my-properties/', views.UserPropertiesView.as_view(), name='my_properties'),
    path('favorites/', views.UserFavoritesView.as_view(), name='favorites'),
    
    # تنظیمات حساب کاربری
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    path('notifications/', views.UserNotificationsView.as_view(), name='notifications'),
]
