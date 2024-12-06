from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),
    
    # Core App URLs
    path('', TemplateView.as_view(template_name='core/home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='core/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='core/contact.html'), name='contact'),
    
    # Properties App URLs
    path('properties/', include('properties.urls', namespace='properties')),
    
    # Users App URLs
    path('users/', include('users.urls', namespace='users')),
    
    # API URLs
    path('api/v1/', include([
        path('properties/', include('properties.api.urls')),
        path('users/', include('users.api.urls')),
    ])),
    
    # Authentication URLs
    path('auth/', include([
        path('', include('django.contrib.auth.urls')),
    ])),
]

# Media and Static Files URLs
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom Error Pages
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'

# Admin Site Customization
admin.site.site_header = 'مدیریت املاک هوشمند'
admin.site.site_title = 'پنل مدیریت'
admin.site.index_title = 'مدیریت سیستم'
