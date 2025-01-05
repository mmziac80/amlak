from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from properties.api.views import PropertyLocationViewSet
from rest_framework.routers import DefaultRouter
from core.views import HomeView

# DRF Router Setup
router = DefaultRouter()
router.register('properties/locations', PropertyLocationViewSet, basename='property-locations')

# API URL Patterns
api_patterns = [
    path('', include(router.urls)),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Core URLs
    path('', HomeView.as_view(), name='home'),
    path('', include('core.urls')),
    
    # Authentication
    path('auth/', include('django.contrib.auth.urls'), name='auth'),
    
    # App URLs
    path('properties/', include('properties.urls', namespace='properties')),  # Remove duplicate
    path('payments/', include('payments.urls', namespace='payments')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('users/', include('users.urls', namespace='users')),
    
    # API URLs
    path('api/', include(api_patterns)),
]

# Static/Media Files in Debug Mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
