from rest_framework import viewsets, filters
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, FloatField, ExpressionWrapper, Q
from django.db.models.functions import Radians, ACos, Cos, Sin
from ..models import Property
from ..serializers import PropertyLocationSerializer
from decimal import Decimal
from django.utils import timezone

class PropertyLocationViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت موقعیت‌های املاک"""
    serializer_class = PropertyLocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['created_at', 'price', 'area', 'distance']
    
    filterset_fields = {
        'deal_type': ['exact'],
        'status': ['exact'],
        'area': ['gte', 'lte'],
        'rooms': ['exact'],
        'parking': ['exact'],
        'elevator': ['exact'],
        'is_featured': ['exact'],
        'is_active': ['exact'],
        'latitude': ['isnull'],
        'longitude': ['isnull'],
        'created_at': ['gte', 'lte'],
        'updated_at': ['gte', 'lte']
    }
    
    search_fields = ['title', 'address', 'description']

    def get_queryset(self):
        """فیلتر کردن نتایج با کش‌گذاری"""
        cache_key = f"property_locations_{self.request.query_params}"
        cached_results = cache.get(cache_key)
        
        if cached_results is not None:
            return cached_results

        queryset = Property.objects.select_related(
            'saleproperty', 
            'rentproperty', 
            'dailyrentproperty'
        ).filter(
            latitude__isnull=False,
            longitude__isnull=False
        )

        filters = Q()
        
        # فیلتر نوع معامله
        deal_type = self.request.query_params.get('deal_type')
        if deal_type:
            filters &= Q(deal_type=deal_type)

        # فیلترهای قیمت
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price or max_price:
            price_filters = Q()
            if min_price:
                price_filters |= Q(saleproperty__total_price__gte=min_price)
                price_filters |= Q(rentproperty__monthly_rent__gte=min_price)
                price_filters |= Q(dailyrentproperty__daily_price__gte=min_price)
            if max_price:
                price_filters |= Q(saleproperty__total_price__lte=max_price)
                price_filters |= Q(rentproperty__monthly_rent__lte=max_price)
                price_filters |= Q(dailyrentproperty__daily_price__lte=max_price)
            filters &= price_filters

        # فیلترهای متراژ
        min_area = self.request.query_params.get('min_area')
        max_area = self.request.query_params.get('max_area')
        if min_area:
            filters &= Q(area__gte=min_area)
        if max_area:
            filters &= Q(area__lte=max_area)

        queryset = queryset.filter(filters)
        cache.set(cache_key, queryset, timeout=300)  # کش برای 5 دقیقه
        return queryset

    @action(detail=False, methods=['get'])
    def locations(self, request):
        """دریافت همه موقعیت‌های املاک"""
        cache_key = f"all_locations_{request.query_params}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        response_data = {
            'results': serializer.data,
            'count': queryset.count()
        }
        
        cache.set(cache_key, response_data, timeout=300)
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """یافتن املاک نزدیک"""
        try:
            lat = float(request.GET.get('latitude'))
            lng = float(request.GET.get('longitude'))
            radius = float(request.GET.get('radius', 5))
            
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                return Response(
                    {"error": "مختصات جغرافیایی نامعتبر است"},
                    status=400
                )

            cache_key = f"nearby_properties_{lat}_{lng}_{radius}"
            cached_results = cache.get(cache_key)
            
            if cached_results:
                return Response(cached_results)

            properties = self.get_queryset().annotate(
                distance=ExpressionWrapper(
                    6371 * ACos(
                        Cos(Radians(lat)) *
                        Cos(Radians(F('latitude'))) *
                        Cos(Radians(F('longitude')) - Radians(lng)) +
                        Sin(Radians(lat)) *
                        Sin(Radians(F('latitude')))
                    ),
                    output_field=FloatField()
                )
            ).filter(
                distance__lte=radius
            ).order_by('distance')

            serializer = self.get_serializer(properties, many=True)
            response_data = {'results': serializer.data}
            
            cache.set(cache_key, response_data, timeout=300)
            return Response(response_data)

        except (ValueError, TypeError):
            return Response(
                {"error": "پارامترهای ورودی نامعتبر هستند"},
                status=400
            )

    @action(detail=False, methods=['get'])
    def cluster(self, request):
        """گروه‌بندی املاک نزدیک به هم"""
        zoom = int(request.GET.get('zoom', 12))
        bounds = request.GET.get('bounds')  # format: "lat1,lng1,lat2,lng2"
        
        if bounds:
            lat1, lng1, lat2, lng2 = map(float, bounds.split(','))
            properties = self.get_queryset().filter(
                latitude__gte=min(lat1, lat2),
                latitude__lte=max(lat1, lat2),
                longitude__gte=min(lng1, lng2),
                longitude__lte=max(lng1, lng2)
            )
        else:
            properties = self.get_queryset()

        # محاسبه گروه‌ها بر اساس zoom level
        grid_size = 0.01 * (2 ** (12 - zoom))  # تنظیم اندازه گرید
        
        clusters = {}
        for prop in properties:
            grid_lat = round(float(prop.latitude) / grid_size) * grid_size
            grid_lng = round(float(prop.longitude) / grid_size) * grid_size
            
            key = f"{grid_lat},{grid_lng}"
            if key not in clusters:
                clusters[key] = {
                    'center': {'lat': grid_lat, 'lng': grid_lng},
                    'count': 0,
                    'properties': []
                }
            
            clusters[key]['count'] += 1
            clusters[key]['properties'].append(prop.id)

        return Response(list(clusters.values()))
