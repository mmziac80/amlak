from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropertyListView,
    PropertyDetailView,
    PropertyCreateView,
    PropertyUpdateView,
    PropertyDeleteView,
    PropertySearchView,
    PropertyViewSet,
    PropertyImageViewSet,
    PropertyFavoriteView,
    PropertyReviewView,
    DailyRentPropertyListView,
    SalePropertyListView,
    RentPropertyListView
)

app_name = 'properties'

# Router برای API ها
router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='api_property')
router.register(r'images', PropertyImageViewSet, basename='api_property_image')

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # نمایش املاک
    path('', PropertyListView.as_view(), name='list'),
    path('daily/', DailyRentPropertyListView.as_view(), name='daily_list'),
    path('sale/', SalePropertyListView.as_view(), name='sale_list'),
    path('rent/', RentPropertyListView.as_view(), name='rent_list'),
    path('detail/<int:pk>/', PropertyDetailView.as_view(), name='detail'),
    
    # مدیریت املاک
    path('manage/', include([
        path('create/', PropertyCreateView.as_view(), name='create'),
        path('update/<int:pk>/', PropertyUpdateView.as_view(), name='update'),
        path('delete/<int:pk>/', PropertyDeleteView.as_view(), name='delete'),
    ])),
    
    # جستجو و علاقه‌مندی‌ها
    path('search/', PropertySearchView.as_view(), name='search'),
    path('favorite/<int:pk>/', PropertyFavoriteView.as_view(), name='favorite'),
    
    # نظرات
    path('review/<int:pk>/', PropertyReviewView.as_view(), name='review'),
]
