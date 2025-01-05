# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model

from rest_framework import serializers
User = get_user_model()  # مدل کاربر را دریافت کن

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp_code = serializers.CharField()

