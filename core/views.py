from django.views.generic import CreateView, TemplateView, ListView
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count

from users.forms import SignUpForm
from properties.models import SaleProperty, RentProperty, DailyRentProperty
from blog.models import Post

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_properties'] = {
            'sale': SaleProperty.objects.filter(is_featured=True)[:6],
            'rent': RentProperty.objects.filter(is_featured=True)[:6],
            'daily': DailyRentProperty.objects.filter(is_featured=True)[:6]
        }
        context['latest_posts'] = Post.objects.filter(status='published')[:3]
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
