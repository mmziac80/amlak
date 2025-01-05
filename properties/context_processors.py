from django.conf import settings

# properties/context_processors.py

def google_maps_api_key(request):
    from django.conf import settings
    return {'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY}

