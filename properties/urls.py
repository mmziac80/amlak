from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import PropertyLocationViewSet
from . import views
from .views import (
    AdvancedSearchView,
)

# تنظیم روتر API
router = DefaultRouter()
router.register('locations', PropertyLocationViewSet, basename='property-locations')

# مسیرهای API
api_urlpatterns = [
    path('', include(router.urls)),
]

# مسیرهای اجاره روزانه
daily_property_patterns = [
    path('', views.DailyRentPropertyListView.as_view(), name='daily_list'),
    path('<int:pk>/', views.DailyRentPropertyDetailView.as_view(), name='daily_detail'),
    path('<int:pk>/book/', views.DailyRentBookingView.as_view(), name='daily_book'),
    path('<int:pk>/calendar/', views.DailyRentCalendarView.as_view(), name='daily_calendar'),
    path('<int:pk>/payment/', views.DailyRentPropertyPaymentView.as_view(), name='daily_payment'),
]

app_name = 'property'

urlpatterns = [
    # مسیرهای اصلی املاک
    path('', views.PropertyListView.as_view(), name='list'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('search/', views.PropertySearchView.as_view(), name='search'),
    
    # مسیرهای املاک فروشی
    path('sale/', views.SalePropertyListView.as_view(), name='sale_properties'),
    path('sale/<int:pk>/', views.SalePropertyDetailView.as_view(), name='sale_detail'),
    path('sale/search/', views.SalePropertySearchView.as_view(), name='sale_search'),
    
    # مسیرهای املاک اجاره‌ای
    path('rent/', views.RentPropertyListView.as_view(), name='rent_properties'),
    path('rent/<int:pk>/', views.RentPropertyDetailView.as_view(), name='rent_detail'),
    path('rent/search/', views.RentPropertySearchView.as_view(), name='rent_search'),
    
    # مسیرهای اجاره روزانه
    path('daily/', include(daily_property_patterns)),
    path('daily/search/', views.DailyRentPropertySearchView.as_view(), name='daily_search'),
    
    # مسیرهای علاقه‌مندی و نظرات
    path('<int:pk>/favorite/', views.PropertyFavoriteView.as_view(), name='favorite'),
    path('<int:pk>/review/', views.PropertyReviewView.as_view(), name='review'),
    
    # جستجوی پیشرفته
    path('properties/advanced-search/', AdvancedSearchView.as_view(), name='advanced_search'),
    
    # مسیرهای فرم ملک
    path('add/', views.PropertyCreateView.as_view(), name='property_create'),
    path('<int:pk>/edit/', views.PropertyUpdateView.as_view(), name='property_update'),
    
    # مسیر آپلود تصاویر
    path('image/upload/', views.PropertyImageUploadView.as_view(), name='property_image_upload'),
    
    # مسیرهای فرم‌های ثبت بازدید
    path('<str:type>/<int:pk>/visit/', views.VisitRequestView.as_view(), name='visit_request'),
    
    # مسیرهای API
    path('api/', include(api_urlpatterns)),
    path('location-filter/', views.PropertyLocationFilter.as_view(), name='location-filter'),
    path('api/nearby/', views.nearby_properties_api, name='nearby-properties-api'),
]
