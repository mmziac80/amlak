from rest_framework import viewsets, status, generics 
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Sum, Avg, F
from django.shortcuts import get_object_or_404

from .models import Payment, Transaction
from .serializers import (
    PaymentSerializer,
    TransactionSerializer,
    PaymentStatusSerializer,
    PaymentRefundSerializer,
    PaymentReportSerializer
)
from .utils import init_payment, verify_payment
from .constants import PAYMENT_STATUS
from .permissions import (
    IsPaymentOwner,
    CanInitiatePayment,
    CanVerifyPayment,
    CanRefundPayment
)
from .mixins import (
    PaymentCacheMixin,
    PaymentValidationMixin,
    TransactionCreateMixin
)
from .filters import PaymentFilter, TransactionFilter
from .pagination import StandardResultsSetPagination

class PaymentViewSet(PaymentCacheMixin, 
                    PaymentValidationMixin,
                    TransactionCreateMixin,
                    viewsets.ModelViewSet):
    """ویوست مدیریت پرداخت‌ها"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsPaymentOwner]
    pagination_class = StandardResultsSetPagination
    filterset_class = PaymentFilter
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[CanInitiatePayment])
    def init(self, request, pk=None):
        """شروع فرآیند پرداخت"""
        payment = self.get_object()
        self.validate_payment(payment)
        
        result = init_payment(payment)
        if result['success']:
            return Response({
                'payment_url': result['payment_url'],
                'authority': result['authority']
            })
        return Response(
            {'error': result['error']},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[CanVerifyPayment])
    def verify(self, request, pk=None):
        """تایید پرداخت"""
        payment = self.get_object()
        result = verify_payment(payment)
        if result['success']:
            return Response({
                'status': 'success',
                'ref_id': result['ref_id']
            })
        return Response(
            {'error': result['error']},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[CanRefundPayment])
    def refund(self, request, pk=None):
        """درخواست استرداد وجه"""
        payment = self.get_object()
        serializer = PaymentRefundSerializer(data=request.data)
        
        if serializer.is_valid():
            payment.request_refund(
                reason=serializer.validated_data['reason'],
                bank_account=serializer.validated_data['bank_account']
            )
            return Response({'status': 'درخواست استرداد ثبت شد'})
            
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ویوست نمایش تراکنش‌ها"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_class = TransactionFilter

    def get_queryset(self):
        return Transaction.objects.filter(payment__user=self.request.user)

class PaymentStatusView(generics.RetrieveAPIView):
    """ویو بررسی وضعیت پرداخت"""
    serializer_class = PaymentStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(
            Payment,
            tracking_code=self.kwargs['tracking_code'],
            user=self.request.user
        )

class PaymentReportView(generics.GenericAPIView):
    """ویو گزارش پرداخت‌ها"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date', timezone.now().date())

        queryset = Payment.objects.filter(user=request.user)
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        queryset = queryset.filter(created_at__date__lte=end_date)

        stats = queryset.aggregate(
            total_count=Count('id'),
            successful_count=Count('id', filter=F('status')=='success'),
            failed_count=Count('id', filter=F('status')=='failed'),
            total_amount=Sum('amount', filter=F('status')=='success'),
            average_amount=Avg('amount', filter=F('status')=='success')
        )

        stats['success_rate'] = (
            stats['successful_count'] / stats['total_count'] * 100 
            if stats['total_count'] > 0 else 0
        )

        serializer = PaymentReportSerializer(stats)
        return Response(serializer.data)