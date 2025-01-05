
from django.urls import path
from . import views

app_name = 'users_api'

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
]
