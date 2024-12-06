from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import View
from django.utils import timezone
from django.db import transaction, models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Payment, Transaction, RefundRequest
from .forms import (
    PaymentFilterForm, 
    PaymentInitiateForm,
    PaymentConfirmForm,
    RefundRequestForm
)
from .serializers import (
    PaymentSerializer, 
    PaymentDetailSerializer,
    RefundRequestSerializer
)
from .utils import init_payment, verify_payment, send_payment_sms
from .constants import PAYMENT_STATUS, SMS_TEMPLATES
from .tasks import settle_with_owner
from properties.models import Property

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(renter=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PaymentDetailSerializer
        return PaymentSerializer

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        payment = self.get_object()
        bank_response = payment.send_to_bank()
        return Response(bank_response)

class RefundRequestViewSet(viewsets.ModelViewSet):
    serializer_class = RefundRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RefundRequest.objects.filter(user=self.request.user)

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
            result = init_payment(payment)
            if result['success']:
                payment.reference_id = result['authority']
                payment.save()
                return redirect(result['payment_url'])
            messages.error(request, result['error'])
        
        return render(request, self.template_name, {'form': form, 'payment': payment})

class PaymentCallbackView(LoginRequiredMixin, View):
    @transaction.atomic
    def get(self, request):
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')
        
        payment = get_object_or_404(Payment, reference_id=authority)
        
        if status == 'OK':
            result = verify_payment(payment)
            if result['success']:
                Transaction.objects.create(
                    payment=payment,
                    amount=payment.total_amount,
                    status=PAYMENT_STATUS['SUCCESS'],
                    tracking_code=result['ref_id']
                )
                
                payment.status = PAYMENT_STATUS['SUCCESS']
                payment.payment_date = timezone.now()
                payment.bank_tracking_code = result['ref_id']
                payment.save()
                
                settle_with_owner.delay(payment.id)
                
                send_payment_sms(
                    payment.renter.phone, 
                    SMS_TEMPLATES['PAYMENT_SUCCESS'].format(
                        tracking_code=payment.bank_tracking_code
                    )
                )
                
                messages.success(request, 'پرداخت با موفقیت انجام شد')
                return redirect('payments:payment_success', payment.id)
            else:
                payment.status = PAYMENT_STATUS['FAILED']
                payment.save()
                messages.error(request, result['error'])
        else:
            payment.status = PAYMENT_STATUS['FAILED']
            payment.save()
            messages.error(request, 'پرداخت ناموفق بود')
            
        return redirect('payments:payment_failed', payment.id)

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        queryset = Payment.objects.filter(renter=self.request.user)
        form = PaymentFilterForm(self.request.GET)
        
        if form.is_valid():
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
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

class PaymentHistoryView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/payment_history.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(
            models.Q(renter=self.request.user) | 
            models.Q(owner=self.request.user)
        ).order_by('-created_at')

class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/payment_detail.html'
    
    def get_object(self):
        payment = get_object_or_404(Payment, id=self.kwargs['payment_id'])
        if not (self.request.user.is_staff or 
                self.request.user in [payment.renter, payment.owner]):
            raise Http404
        return payment

class PaymentSuccessView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/payment_success.html'
    context_object_name = 'payment'

    def get_object(self):
        return get_object_or_404(
            Payment,
            id=self.kwargs['payment_id'],
            status=PAYMENT_STATUS['SUCCESS']
        )

class PaymentFailedView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/payment_failed.html'
    context_object_name = 'payment'

class PaymentReceiptView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/payment_receipt.html'
    context_object_name = 'payment'

    def get_object(self):
        payment = get_object_or_404(
            Payment,
            id=self.kwargs['payment_id'],
            status=PAYMENT_STATUS['SUCCESS']
        )
        if not (self.request.user.is_staff or 
                self.request.user in [payment.renter, payment.owner]):
            raise Http404
        return payment

class RefundRequestView(LoginRequiredMixin, CreateView):
    model = RefundRequest
    form_class = RefundRequestForm
    template_name = 'payments/refund_request.html'
    success_url = reverse_lazy('payments:payment_list')
    
    def form_valid(self, form):
        refund = form.save(commit=False)
        refund.payment = get_object_or_404(Payment, pk=self.kwargs['payment_id'])
        refund.user = self.request.user
        refund.save()
        messages.success(self.request, 'درخواست استرداد با موفقیت ثبت شد')
        return super().form_valid(form)
