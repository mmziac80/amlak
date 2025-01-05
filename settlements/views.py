# -*- coding: utf-8 -*-

from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from datetime import timedelta

from .models import Settlement
from .forms import SettlementCreateForm, SettlementFilterForm
from .services import SettlementService, ReportService
from .filters import SettlementFilter

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class SettlementListView(LoginRequiredMixin, ListView):
    model = Settlement
    template_name = 'settlements/settlement_list.html'
    context_object_name = 'settlements'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Settlement.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
            
        self.filterset = SettlementFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.select_related('owner', 'processed_by')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['filter_form'] = SettlementFilterForm(self.request.GET)
        
        queryset = self.filterset.qs
        context['total_amount'] = queryset.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        context['pending_count'] = queryset.filter(status='pending').count()
        context['completed_count'] = queryset.filter(status='completed').count()
        
        return context

class SettlementDetailView(LoginRequiredMixin, DetailView):
    model = Settlement
    template_name = 'settlements/settlement_detail.html'
    context_object_name = 'settlement'
    slug_field = 'tracking_code'
    slug_url_kwarg = 'tracking_code'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset.select_related('owner', 'processed_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_cancel'] = self.object.status == 'pending'
        context['can_process'] = self.request.user.is_staff and self.object.status == 'pending'
        return context

class SettlementCreateView(LoginRequiredMixin, CreateView):
    model = Settlement
    template_name = 'settlements/settlement_create.html'
    form_class = SettlementCreateForm
    success_url = reverse_lazy('settlements:settlement-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = 'pending'
        response = super().form_valid(form)
        messages.success(self.request, 'درخواست تسویه با موفقیت ثبت شد')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class SettlementDashboardView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = 'settlements/settlement_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        settlements = Settlement.objects.all()
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_settlements = settlements.filter(created_at__gte=thirty_days_ago)

        # آمار کلی
        context.update({
            'total_settlements': settlements.count(),
            'total_amount': settlements.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
            'pending_count': settlements.filter(status='pending').count(),
            'completed_count': settlements.filter(status='completed').count(),
            'failed_count': settlements.filter(status='failed').count(),
        })
        
        # نرخ موفقیت
        total_processed = context['completed_count'] + context['failed_count']
        context['success_rate'] = round((context['completed_count'] / total_processed * 100) if total_processed > 0 else 0)
        
        # آمار روزانه
        daily_data = recent_settlements.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('date')

        context.update({
            'chart_labels': [d['date'].strftime('%Y-%m-%d') for d in daily_data],
            'chart_data': [float(d['total'] or 0) for d in daily_data],
            'recent_settlements': settlements.select_related('owner').order_by('-created_at')[:10]
        })
        
        return context

class SettlementHistoryView(LoginRequiredMixin, DetailView):
    model = Settlement
    template_name = 'settlements/settlement_history.html'
    slug_field = 'tracking_code'
    slug_url_kwarg = 'tracking_code'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset

@method_decorator(require_POST, name='dispatch')
class SettlementCancelView(LoginRequiredMixin, DetailView):
    model = Settlement
    slug_field = 'tracking_code'
    slug_url_kwarg = 'tracking_code'
    
    def post(self, request, *args, **kwargs):
        settlement = self.get_object()
        if settlement.status != 'pending':
            messages.error(request, 'فقط درخواست‌های در انتظار قابل لغو هستند')
            return redirect('settlements:settlement-detail', tracking_code=settlement.tracking_code)
            
        if settlement.owner != request.user and not request.user.is_staff:
            messages.error(request, 'شما دسترسی لازم برای این عملیات را ندارید')
            return redirect('settlements:settlement-detail', tracking_code=settlement.tracking_code)
            
        settlement.mark_as_cancelled(processed_by=request.user)
        messages.success(request, 'درخواست تسویه با موفقیت لغو شد')
        return redirect('settlements:settlement-list')

class SettlementPrintView(LoginRequiredMixin, DetailView):
    model = Settlement
    template_name = 'settlements/settlement_print.html'
    slug_field = 'tracking_code'
    slug_url_kwarg = 'tracking_code'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset

class SettlementDownloadView(LoginRequiredMixin, DetailView):
    model = Settlement
    slug_field = 'tracking_code'
    slug_url_kwarg = 'tracking_code'
    
    def get(self, request, *args, **kwargs):
        settlement = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="settlement_{settlement.tracking_code}.pdf"'
        
        # اینجا منطق تولید PDF را اضافه کنید
        
        return response

def settlement_403_error(request, exception):
    return render(request, 'settlements/errors/403.html', status=403)

def settlement_404_error(request, exception):
    return render(request, 'settlements/errors/404.html', status=404)

def settlement_500_error(request):
    return render(request, 'settlements/errors/500.html', status=500)

