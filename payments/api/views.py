# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from .models import Payment, Property, Transaction, Settlement
from .forms import PaymentInitiateForm, PaymentConfirmForm, PaymentFilterForm
from .tasks import process_owner_settlement
from .serializers import CommissionRateSerializer, PaymentSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(
            models.Q(renter=self.request.user) | 
            models.Q(owner=self.request.user)
        )

class PaymentInitiateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentInitiateForm
    template_name = 'payments/payment_initiate.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['property'] = get_object_or_404(Property, pk=self.kwargs['property_id'])
        return kwargs
        
    def form_valid(self, form):
        payment = form.save(commit=False)
        payment.property = form.property
        payment.renter = self.request.user
        payment.owner = payment.property.owner
        payment.calculate_amounts()
        payment.save()
        
        return redirect('payments:payment_confirm', payment.id)

class PaymentConfirmView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/payment_confirm.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PaymentConfirmForm()
        return context
    
    def post(self, request, *args, **kwargs):
        payment = self.get_object()
        form = PaymentConfirmForm(request.POST)
        
        if form.is_valid():
            bank_response = payment.send_to_bank()
            if bank_response['status'] == 'success':
                return redirect(bank_response['payment_url'])
            
        messages.error(request, 'خطا در اتصال به درگاه پرداخت')
        return render(request, self.template_name, {'form': form, 'payment': payment})

class PaymentCallbackView(TemplateView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        tracking_code = request.POST.get('tracking_code')
        status = request.POST.get('status')
        
        try:
            payment = Payment.objects.get(payment_tracking_code=tracking_code)
            
            if status == 'success':
                payment.payment_status = 'paid'
                payment.payment_date = timezone.now()
                payment.save()
                
                # شروع فرآیند تسویه با مالک
                process_owner_settlement.delay(payment.id)
                
                return redirect('payments:payment_success', payment.id)
            else:
                payment.payment_status = 'failed'
                payment.save()
                return redirect('payments:payment_failed', payment.id)
                
        except Payment.DoesNotExist:
            return HttpResponse('پرداخت نامعتبر', status=400)

class PaymentSuccessView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/success.html'
    pk_url_kwarg = 'payment_id'

class PaymentFailedView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/failed.html'
    pk_url_kwarg = 'payment_id'

class PaymentReceiptView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/receipt.html'
    pk_url_kwarg = 'payment_id'

class PaymentHistoryView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/history.html'
    context_object_name = 'payments'
    paginate_by = 10
    
    def get_queryset(self):
        return Payment.objects.filter(renter=self.request.user).order_by('-created_at')

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/list.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        queryset = Payment.objects.all()
        form = PaymentFilterForm(self.request.GET)
        
        if form.is_valid():
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(payment_status=form.cleaned_data['status'])
            if form.cleaned_data.get('min_amount'):
                queryset = queryset.filter(total_amount__gte=form.cleaned_data['min_amount'])
            if form.cleaned_data.get('max_amount'):
                queryset = queryset.filter(total_amount__lte=form.cleaned_data['max_amount'])
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(created_at__date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data.get('date_to'):
                queryset = queryset.filter(created_at__date__lte=form.cleaned_data['date_to'])
                
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = PaymentFilterForm(self.request.GET)
        return context

class CommissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = CommissionRateSerializer
    queryset = Property.objects.all()

    @action(detail=True, methods=['patch'])
    def update_rate(self, request, pk=None):
        property = self.get_object()
        serializer = CommissionRateSerializer(data=request.data)
        
        if serializer.is_valid():
            property.commission_rate = serializer.validated_data['commission_rate']
            property.save()
            return Response({'status': 'نرخ کمیسیون بروزرسانی شد'})
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

