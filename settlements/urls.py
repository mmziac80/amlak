from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import views as api_views

router = DefaultRouter()
router.register(r'settlements', api_views.SettlementViewSet, basename='api-settlement')

app_name = 'settlements'

urlpatterns = [
    # API URLs
    path('api/', include([
        path('', include(router.urls)),
        path('chart-data/', api_views.ChartDataView.as_view(), name='chart-data'),
        path('reports/', api_views.SettlementReportView.as_view(), name='settlement-reports'),
        path('bulk-action/', api_views.SettlementBulkActionView.as_view(), name='settlement-bulk-action'),
    ])),
    
    # Web URLs
    path('', views.SettlementListView.as_view(), name='settlement-list'),
    path('create/', views.SettlementCreateView.as_view(), name='settlement-create'),
    path('detail/<str:tracking_code>/', views.SettlementDetailView.as_view(), name='settlement-detail'),
    path('dashboard/', views.SettlementDashboardView.as_view(), name='settlement-dashboard'),
    path('history/<str:tracking_code>/', views.SettlementHistoryView.as_view(), name='settlement-history'),
    path('print/<str:tracking_code>/', views.SettlementPrintView.as_view(), name='settlement-print'),
    path('download/<str:tracking_code>/', views.SettlementDownloadView.as_view(), name='settlement-download'),
    
    # Process URLs
    path('process/', include([
        path('cancel/<str:tracking_code>/', views.SettlementCancelView.as_view(), name='settlement-cancel'),
        path('verify/<str:tracking_code>/', api_views.SettlementVerifyView.as_view(), name='settlement-verify'),
    ])),
]

# Error handlers
handler403 = 'settlements.views.settlement_403_error'
handler404 = 'settlements.views.settlement_404_error'
handler500 = 'settlements.views.settlement_500_error'
