
from rest_framework.views import APIView
from rest_framework.response import Response
from ..serializers import UserRegistrationSerializer, VerifyOTPSerializer

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'ثبت نام با موفقیت انجام شد'})
        return Response(serializer.errors, status=400)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            # منطق تایید OTP
            return Response({'message': 'کد تایید شد'})
        return Response(serializer.errors, status=400)

class UserProfileView(APIView):
    def get(self, request):
        # منطق نمایش پروفایل
        return Response({'user': 'profile data'})
