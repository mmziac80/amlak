# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import CreateView, TemplateView, ListView
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.core.serializers import serialize
import json
from django.http import JsonResponse

from users.forms import SignUpForm
from properties.models import SaleProperty, RentProperty, DailyRentProperty, Property
from blog.models import Post
from django.conf import settings
class HomeView(TemplateView):
    template_name = 'core/home.html'
    NESHAN_API_KEY = 'web.ea06affc328a4934995818fed7a98b78'

    def get_property_data(self, property_obj, deal_type):
        """متد کمکی برای تبدیل اطلاعات ملک به دیکشنری"""
        price_display = {
            'sale': lambda x: str(x.total_price) if hasattr(x, 'total_price') else '',
            'rent': lambda x: f"ودیعه: {x.deposit} - اجاره: {x.monthly_rent}" if hasattr(x, 'deposit') else '',
            'daily': lambda x: f"اجاره روزانه: {x.daily_price}" if hasattr(x, 'daily_price') else ''
        }

        return {
            'title': property_obj.title,
            'price': price_display[deal_type](property_obj),
            'latitude': float(property_obj.latitude) if property_obj.latitude else None,
            'longitude': float(property_obj.longitude) if property_obj.longitude else None,
            'type': deal_type,
            'image': property_obj.images.first().image.url if property_obj.images.exists() else '',
            'url': property_obj.get_absolute_url(),
            'address': property_obj.address,
            'district': property_obj.district,
            'property_type': property_obj.get_property_type_display(),
            'area': property_obj.area,
            'rooms': property_obj.rooms
        }


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['NESHAN_API_KEY'] = self.NESHAN_API_KEY
        
        # بهینه‌سازی کوئری‌ها
        property_queries = {
            'sale': SaleProperty.objects.select_related('owner').prefetch_related('images'),
            'rent': RentProperty.objects.select_related('owner').prefetch_related('images'),
            'daily': DailyRentProperty.objects.select_related('owner').prefetch_related('images')
        }

        all_properties = []
        featured_properties = {}

        # جمع‌آوری داده‌ها در یک حلقه
        for deal_type, query in property_queries.items():
            properties = query.all()
            all_properties.extend([
                self.get_property_data(prop, deal_type) 
                for prop in properties
            ])
            featured_properties[deal_type] = properties.filter(is_featured=True)[:6]

        context['properties_json'] = json.dumps(all_properties)
        context['featured_properties'] = featured_properties

        return context






class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['properties_count'] = {
            'sale': SaleProperty.objects.filter(owner=user).count(),
            'rent': RentProperty.objects.filter(owner=user).count(),
            'daily': DailyRentProperty.objects.filter(owner=user).count()
        }
        
        context['favorites_count'] = {
            'sale': user.favorite_sales.count(),
            'rent': user.favorite_rents.count(),
            'daily': user.favorite_dailies.count()
        }

        context['recent_properties'] = {
            'sale': SaleProperty.objects.filter(owner=user).order_by('-created_at')[:5],
            'rent': RentProperty.objects.filter(owner=user).order_by('-created_at')[:5],
            'daily': DailyRentProperty.objects.filter(owner=user).order_by('-created_at')[:5]
        }

        return context


class AboutView(TemplateView):
    template_name = 'core/about.html'

class ContactView(TemplateView):
    template_name = 'core/contact.html'

class PrivacyView(TemplateView):
    template_name = 'core/privacy.html'

class TermsView(TemplateView):
    template_name = 'core/terms.html'

class FAQView(TemplateView):
    template_name = 'core/faq.html'

class StatsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # آمار کلی املاک
        context['total_properties'] = {
            'sale': SaleProperty.objects.count(),
            'rent': RentProperty.objects.count(),
            'daily': DailyRentProperty.objects.count()
        }

        # آمار به تفکیک مناطق
        context['district_stats'] = {
            'sale': SaleProperty.objects.values('district').annotate(count=Count('id')),
            'rent': RentProperty.objects.values('district').annotate(count=Count('id')),
            'daily': DailyRentProperty.objects.values('district').annotate(count=Count('id'))
        }

        # آمار به تفکیک نوع ملک
        context['type_stats'] = {
            'sale': SaleProperty.objects.values('property_type').annotate(count=Count('id')),
            'rent': RentProperty.objects.values('property_type').annotate(count=Count('id')),
            'daily': DailyRentProperty.objects.values('property_type').annotate(count=Count('id'))
        }

        return context


class SearchView(ListView):
    template_name = 'core/search_results.html'
    context_object_name = 'results'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        property_type = self.request.GET.get('type', 'all')
        
        if property_type == 'sale':
            return SaleProperty.objects.filter(title__icontains=query)
        elif property_type == 'rent':
            return RentProperty.objects.filter(title__icontains=query)
        elif property_type == 'daily':
            return DailyRentProperty.objects.filter(title__icontains=query)
        else:
            sale = SaleProperty.objects.filter(title__icontains=query)
            rent = RentProperty.objects.filter(title__icontains=query)
            daily = DailyRentProperty.objects.filter(title__icontains=query)
            return list(sale) + list(rent) + list(daily)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['property_type'] = self.request.GET.get('type', 'all')
        return context
def property_locations_api(request):
    # دریافت نوع ملک از پارامترهای درخواست
    property_type = request.GET.get('type', 'all')

    # انتخاب مدل مناسب بر اساس نوع ملک با فیلتر موقعیت جغرافیایی
    base_query = {
        'latitude__isnull': False,
        'longitude__isnull': False
    }

    if property_type == 'sale':
        properties = SaleProperty.objects.filter(**base_query)
    elif property_type == 'rent':
        properties = RentProperty.objects.filter(**base_query)
    elif property_type == 'daily':
        properties = DailyRentProperty.objects.filter(**base_query)
    else:
        properties = Property.objects.filter(**base_query)

    # بهینه‌سازی کوئری با select_related و prefetch_related
    properties = properties.select_related('owner').prefetch_related('images')

    # استفاده از متد to_map_data برای آماده‌سازی داده‌ها
    data = [prop.to_map_data() for prop in properties]

    return JsonResponse(data, safe=False)


def custom_404(request, exception):
    return render(request, 'core/404.html', status=404)

def custom_500(request):
    return render(request, 'core/500.html', status=500)
