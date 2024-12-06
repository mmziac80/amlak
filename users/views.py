from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from .models import Property, PropertyImage
from .forms import PropertyForm, PropertySearchForm

class PropertyListView(ListView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 12

    def get_queryset(self):
        queryset = Property.objects.all().order_by('-created_at')
        query = self.request.GET.get('q')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(address__icontains=query)
            )
            
        return queryset

class PropertyDetailView(DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['similar_properties'] = Property.objects.filter(
            property_type=self.object.property_type,
            district=self.object.district
        ).exclude(id=self.object.id)[:3]
        return context

class PropertyCreateView(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    success_url = reverse_lazy('property_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        
        # Handle multiple images
        images = self.request.FILES.getlist('images')
        for image in images:
            PropertyImage.objects.create(
                property=self.object,
                image=image,
                is_main=False
            )
        return response

class PropertyUpdateView(LoginRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    success_url = reverse_lazy('property_list')

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)

class PropertyDeleteView(LoginRequiredMixin, DeleteView):
    model = Property
    success_url = reverse_lazy('property_list')
    template_name = 'properties/property_confirm_delete.html'

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)

@login_required
def add_to_favorites(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if property in request.user.profile.favorites.all():
        request.user.profile.favorites.remove(property)
        added = False
    else:
        request.user.profile.favorites.add(property)
        added = True
    return JsonResponse({'added': added})

@login_required
def my_properties(request):
    properties = Property.objects.filter(owner=request.user)
    return render(request, 'properties/my_properties.html', {
        'properties': properties
    })

@login_required
def favorite_properties(request):
    properties = request.user.profile.favorites.all()
    return render(request, 'properties/favorite_properties.html', {
        'properties': properties
    })

def search_properties(request):
    form = PropertySearchForm(request.GET)
    properties = Property.objects.all()

    if form.is_valid():
        if form.cleaned_data.get('property_type'):
            properties = properties.filter(property_type=form.cleaned_data['property_type'])
        if form.cleaned_data.get('district'):
            properties = properties.filter(district=form.cleaned_data['district'])
        if form.cleaned_data.get('min_price'):
            properties = properties.filter(price__gte=form.cleaned_data['min_price'])
        if form.cleaned_data.get('max_price'):
            properties = properties.filter(price__lte=form.cleaned_data['max_price'])
        if form.cleaned_data.get('min_area'):
            properties = properties.filter(area__gte=form.cleaned_data['min_area'])
        if form.cleaned_data.get('max_area'):
            properties = properties.filter(area__lte=form.cleaned_data['max_area'])

    return render(request, 'properties/search_results.html', {
        'form': form,
        'properties': properties
    })

def property_compare(request):
    if request.method == 'POST':
        property_ids = request.POST.getlist('property_ids')
        properties = Property.objects.filter(id__in=property_ids)
        return render(request, 'properties/compare.html', {
            'properties': properties
        })
    return redirect('property_list')
