# -*- coding: utf-8 -*-

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from .models import Settlement


from ..models import  settlements
from ..serializers import (
    SettlementSerializer,
    SettlementCreateSerializer, 
    SettlementStatusSerializer,
    SettlementReportSerializer,
    SettlementDetailSerializer,
   
)
from ..services import SettlementService, NotificationService
from ..filters import SettlementFilter

class SettlementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SettlementSerializer
    filterset_class = SettlementFilter
    lookup_field = 'tracking_code'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Settlement.objects.all()
        return Settlement.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return SettlementCreateSerializer
        if self.action == 'status':
            return SettlementStatusSerializer
        if self.action == 'retrieve':
            return SettlementDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        settlement = serializer.save(owner=self.request.user)
        NotificationService().send_settlement_notification(settlement)
        return settlement

    @action(detail=True, methods=['get'])
    def status(self, request, tracking_code=None):
        settlement = self.get_object()
        serializer = self.get_serializer(settlement)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def process(self, request, tracking_code=None):
        settlement = self.get_object()
        if not request.user.is_staff:
            raise ValidationError("شما دسترسی لازم برای این عملیات را ندارید")
            
        service = SettlementService()
        result = service.process_settlement(settlement)
        
        if result['status'] == 'success':
            return Response({'status': 'success'})
        return Response({'status': 'failed', 'error': result['error']})

    @action(detail=True, methods=['post'])
    def reject(self, request, tracking_code=None):
        settlement = self.get_object()
        if not request.user.is_staff:
            raise ValidationError("شما دسترسی لازم برای این عملیات را ندارید")
            
        reason = request.data.get('reason')
        if not reason:
            raise ValidationError("دلیل رد درخواست را وارد کنید")
            
        service = SettlementService()
        result = service.reject_settlement(settlement, reason)
        
        if result['status'] == 'success':
            return Response({'status': 'success'})
        return Response({'status': 'failed', 'error': result['error']})

class ChartDataView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        period = request.GET.get('period', 'monthly')
        settlements = Settlement.objects.all()
        
        if period == 'daily':
            days = 30
        elif period == 'weekly':
            days = 90
        else:
            days = 365
            
        start_date = timezone.now() - timedelta(days=days)
        data = settlements.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Sum('amount')
        ).order_by('date')
        
        return Response({
            'labels': [item['date'].strftime('%Y-%m-%d') for item in data],
            'values': [float(item['total']) for item in data]
        })

class SettlementReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        queryset = Settlement.objects.all()
        data = {
            'total_count': queryset.count(),
            'successful_count': queryset.filter(status='completed').count(),
            'failed_count': queryset.filter(status='failed').count(),
            'total_amount': queryset.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
            'average_amount': queryset.filter(status='completed').aggregate(Avg('amount'))['amount__avg'] or 0
        }
        serializer = SettlementReportSerializer(data)
        return Response(serializer.data)

class SettlementBulkActionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        action = request.data.get('action')
        settlement_ids = request.data.get('settlement_ids', [])
        
        settlements = Settlement.objects.filter(tracking_code__in=settlement_ids)
        service = SettlementService()
        
        if action == 'process':
            for settlement in settlements:
                service.process_settlement(settlement)
        elif action == 'reject':
            reason = request.data.get('reason', '')
            for settlement in settlements:
                service.reject_settlement(settlement, reason)
                
        return Response({'status': 'success'})

class SettlementStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        queryset = Settlement.objects.all()
        return Response({
            'status_counts': dict(queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'daily_amounts': dict(
                queryset.filter(status='completed')
                .annotate(date=TruncDate('created_at'))
                .values('date')
                .annotate(total=Sum('amount'))
                .values_list('date', 'total')
            )
        })

class SettlementVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, tracking_code):
        settlement = get_object_or_404(Settlement, tracking_code=tracking_code)
        service = SettlementService()
        result = service.verify_settlement(settlement)
        
        return Response({
            'status': result['status'],
            'bank_reference_id': settlement.bank_reference_id,
            'verified_at': settlement.settled_at
        })

