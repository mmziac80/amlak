# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.utils import timezone
from datetime import timedelta

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import User, UserProfile, UserNotification, UserDevice
from .forms import (
    PhoneLoginForm, 
    OTPVerifyForm,
    UserProfileForm,
    IdentityVerificationForm
)
from .utils import generate_otp, send_sms, is_otp_valid
from .serializers import UserRegistrationSerializer, VerifyOTPSerializer
class PhoneLoginView(View):
    """ورود با شماره تلفن همراه"""
    template_name = 'users/phone_login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('users:profile')
        form = PhoneLoginForm()
        return render(request, self.template_name, {'form': form})
        
    def post(self, request):
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            user, created = User.objects.get_or_create(phone=phone)
            
            otp = generate_otp()
            user.otp = otp
            user.otp_create_time = timezone.now()
            user.save()
            
            send_sms(phone, f'کد تایید شما: {otp}')
            request.session['auth_phone'] = phone
            
            messages.success(request, 'کد تایید ارسال شد')
            return redirect('users:verify-otp')
            
        return render(request, self.template_name, {'form': form})

class VerifyOTPView(View):
    """تایید کد OTP"""
    template_name = 'users/verify_otp.html'
    
    def get(self, request):
        if 'auth_phone' not in request.session:
            messages.error(request, 'لطفا شماره موبایل خود را وارد کنید')
            return redirect('users:phone-login')
        form = OTPVerifyForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            phone = request.session.get('auth_phone')
            user = User.objects.get(phone=phone)
            otp = form.cleaned_data['otp']
            
            if is_otp_valid(user, otp):
                user.is_phone_verified = True
                user.save()
                login(request, user)
                del request.session['auth_phone']
                messages.success(request, 'ورود موفق')
                return redirect('users:profile')
            else:
                messages.error(request, 'کد وارد شده نامعتبر است')
                
        return render(request, self.template_name, {'form': form})

class ProfileView(LoginRequiredMixin, DetailView):
    """نمایش پروفایل کاربر"""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = self.request.user.notifications.filter(is_read=False)[:5]
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """ویرایش پروفایل کاربر"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_update.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'پروفایل شما با موفقیت بروزرسانی شد')
        return super().form_valid(form)

@login_required
def verify_identity(request):
    """احراز هویت کاربر"""
    if request.method == 'POST':
        form = IdentityVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            request.user.identity_document = form.cleaned_data['identity_document']
            request.user.save()
            messages.success(request, 'مدارک شما با موفقیت ثبت شد')
            return redirect('users:profile')
    else:
        form = IdentityVerificationForm()
    
    return render(request, 'users/verify_identity.html', {'form': form})

@login_required
def notifications_list(request):
    """لیست اعلان‌های کاربر"""
    notifications = request.user.notifications.all()
    return render(request, 'users/notifications.html', {
        'notifications': notifications
    })

@login_required
def notification_read(request, pk):
    """علامت‌گذاری اعلان به عنوان خوانده شده"""
    notification = get_object_or_404(UserNotification, pk=pk, user=request.user)
    notification.mark_as_read()
    return redirect('users:notifications')

@api_view(['POST'])
def register_api(request):
    """API ثبت‌نام کاربر"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'کد تایید ارسال شد',
            'user_id': user.id
        })
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def verify_otp_api(request):
    """API تایید کد OTP"""
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data['phone']
        otp = serializer.validated_data['otp']
        user = get_object_or_404(User, phone=phone)
        
        if is_otp_valid(user, otp):
            return Response({'message': 'تایید شد'})
        return Response({'error': 'کد نامعتبر است'}, status=400)
    return Response(serializer.errors, status=400)

def logout_view(request):
    """خروج کاربر از حساب کاربری"""
    logout(request)
    messages.success(request, 'با موفقیت خارج شدید')
    return redirect('users:phone-login')
