from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    SaleProperty,
    RentProperty,
    DailyRentProperty,
    PropertyImage,
    Visit,
    Booking,
    PropertyAvailability
)
from .serializers import (
     PropertySerializer, 
    SalePropertySerializer,
    RentPropertySerializer,
    DailyRentPropertySerializer,
    PropertyImageSerializer,
    VisitSerializer,
    BookingSerializer
)
from .filters import (
    SalePropertyFilter,
    RentPropertyFilter,
    DailyRentPropertyFilter,
    PropertySearchFilter
)
from .forms import (
    SalePropertyForm,
    RentPropertyForm,
    DailyRentPropertyForm,
    PropertySearchForm,
    VisitRequestForm,
    BookingForm
)

class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        property_type = self.request.query_params.get('type', 'sale')
        if property_type == 'sale':
            return SaleProperty.objects.all()
        elif property_type == 'rent':
            return RentProperty.objects.all()
        return DailyRentProperty.objects.all()

    def get_serializer_class(self):
        property_type = self.request.query_params.get('type', 'sale')
        if property_type == 'sale':
            return SalePropertySerializer
        elif property_type == 'rent':
            return RentPropertySerializer
        return DailyRentPropertySerializer

    def get_filterset_class(self):
        property_type = self.request.query_params.get('type', 'sale')
        if property_type == 'sale':
            return SalePropertyFilter
        elif property_type == 'rent':
            return RentPropertyFilter
        return DailyRentPropertyFilter

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        property = self.get_object()
        user = request.user
        
        if property.favorites.filter(id=user.id).exists():
            property.favorites.remove(user)
            return Response({'status': 'removed'})
        else:
            property.favorites.add(user)
            return Response({'status': 'added'})

class SalePropertyViewSet(viewsets.ModelViewSet):
    queryset = SaleProperty.objects.all()
    serializer_class = SalePropertySerializer
    filterset_class = SalePropertyFilter
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class RentPropertyViewSet(viewsets.ModelViewSet):
    queryset = RentProperty.objects.all()
    serializer_class = RentPropertySerializer
    filterset_class = RentPropertyFilter
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class DailyRentPropertyViewSet(viewsets.ModelViewSet):
    queryset = DailyRentProperty.objects.all()
    serializer_class = DailyRentPropertySerializer
    filterset_class = DailyRentPropertyFilter
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [IsAuthenticated]

class VisitViewSet(viewsets.ModelViewSet):
    serializer_class = VisitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Visit.objects.all()
        return Visit.objects.filter(visitor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(visitor=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class HomeView(ListView):
    template_name = 'properties/home.html'
    context_object_name = 'featured_properties'

    def get_queryset(self):
        return {
            'sale': SaleProperty.objects.filter(is_featured=True)[:3],
            'rent': RentProperty.objects.filter(is_featured=True)[:3],
            'daily': DailyRentProperty.objects.filter(is_featured=True)[:3]
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PropertySearchForm()
        return context

class PropertyListView(ListView):
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 12

    def get_queryset(self):
        property_type = self.kwargs.get('type', 'sale')
        if property_type == 'sale':
            queryset = SaleProperty.objects.all()
        elif property_type == 'rent':
            queryset = RentProperty.objects.all()
        else:
            queryset = DailyRentProperty.objects.all()

        form = PropertySearchForm(self.request.GET)
        if form.is_valid():
            return form.filter_queryset(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PropertySearchForm(self.request.GET)
        context['property_type'] = self.kwargs.get('type', 'sale')
        return context

class PropertyDetailView(DetailView):
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'

    def get_queryset(self):
        property_type = self.kwargs.get('type')
        if property_type == 'sale':
            return SaleProperty.objects.all()
        elif property_type == 'rent':
            return RentProperty.objects.all()
        return DailyRentProperty.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property_obj = self.object
        
        context['similar_properties'] = type(property_obj).objects.filter(
            property_type=property_obj.property_type,
            district=property_obj.district
        ).exclude(id=property_obj.id)[:3]
        
        if isinstance(property_obj, DailyRentProperty):
            context['availability'] = PropertyAvailability.objects.filter(
                property=property_obj,
                date__gte=timezone.now().date()
            )
            context['booking_form'] = BookingForm()
        
        if self.request.user.is_authenticated:
            context['visit_form'] = VisitRequestForm()
            
        return context

class PropertyCreateView(LoginRequiredMixin, CreateView):
    template_name = 'properties/property_form.html'

    def get_form_class(self):
        property_type = self.kwargs.get('type')
        if property_type == 'sale':
            return SalePropertyForm
        elif property_type == 'rent':
            return RentPropertyForm
        return DailyRentPropertyForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        
        images = self.request.FILES.getlist('images')
        for image in images:
            PropertyImage.objects.create(
                property=self.object,
                image=image
            )
            
        return response

class PropertyUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'properties/property_form.html'

    def get_queryset(self):
        property_type = self.kwargs.get('type')
        if property_type == 'sale':
            return SaleProperty.objects.filter(owner=self.request.user)
        elif property_type == 'rent':
            return RentProperty.objects.filter(owner=self.request.user)
        return DailyRentProperty.objects.filter(owner=self.request.user)

    def get_form_class(self):
        property_type = self.kwargs.get('type')
        if property_type == 'sale':
            return SalePropertyForm
        elif property_type == 'rent':
            return RentPropertyForm
        return DailyRentPropertyForm

class PropertyDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'properties/property_confirm_delete.html'
    
    def get_queryset(self):
        property_type = self.kwargs.get('type')
        if property_type == 'sale':
            return SaleProperty.objects.filter(owner=self.request.user)
        elif property_type == 'rent':
            return RentProperty.objects.filter(owner=self.request.user)
        return DailyRentProperty.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('properties:list', kwargs={'type': self.kwargs.get('type')})

class VisitRequestView(LoginRequiredMixin, CreateView):
    model = Visit
    form_class = VisitRequestForm
    template_name = 'properties/visit_form.html'

    def form_valid(self, form):
        form.instance.visitor = self.request.user
        form.instance.property = get_object_or_404(
            self.get_property_model(),
            pk=self.kwargs['pk']
        )
        return super().form_valid(form)

    def get_property_model(self):
        property_type = self.kwargs.get('type')
        if property_type == 'sale':
            return SaleProperty
        elif property_type == 'rent':
            return RentProperty
        return DailyRentProperty

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'properties/booking_form.html'

    def form_valid(self, form):
        property_obj = get_object_or_404(DailyRentProperty, pk=self.kwargs['pk'])
        form.instance.property = property_obj
        form.instance.user = self.request.user
        form.instance.total_price = property_obj.calculate_price(
            form.cleaned_data['check_in_date'],
            form.cleaned_data['check_out_date']
        )
        return super().form_valid(form)

class PropertySearchView(ListView):
    template_name = 'properties/search_results.html'
    context_object_name = 'properties'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q')
        property_type = self.request.GET.get('type', 'all')
        
        if query:
            filters = Q(title__icontains=query) | \
                     Q(description__icontains=query) | \
                     Q(address__icontains=query)
            
            if property_type == 'sale':
                return SaleProperty.objects.filter(filters)
            elif property_type == 'rent':
                return RentProperty.objects.filter(filters)
            elif property_type == 'daily':
                return DailyRentProperty.objects.filter(filters)
            else:
                sale = SaleProperty.objects.filter(filters)
                rent = RentProperty.objects.filter(filters)
                daily = DailyRentProperty.objects.filter(filters)
                return list(sale) + list(rent) + list(daily)
                
        return []

class FavoriteListView(LoginRequiredMixin, ListView):
    template_name = 'properties/favorites.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        user = self.request.user
        return {
            'sale': SaleProperty.objects.filter(favorites=user),
            'rent': RentProperty.objects.filter(favorites=user),
            'daily': DailyRentProperty.objects.filter(favorites=user)
        }
