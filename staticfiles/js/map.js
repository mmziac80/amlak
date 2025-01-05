// static/js/map.js
import { MapComponent, MapTypes } from '@neshan-maps-platform/mapbox-gl-vue';

// تنظیمات اولیه نقشه
const mapConfig = {
    mapKey: 'web.ea06affc328a4934995818fed7a98b78',
    center: [36.2972, 59.6067],
    zoom: 13,
    poi: true,
    traffic: false,
    mapType: MapTypes.STANDARD_DAY  // استفاده از enum های استاندارد SDK
};


// ایجاد نقشه
const initMap = () => {
    const map = new NeshanMap({
        container: 'propertyMap',
        ...mapConfig
    });

    // اضافه کردن کنترل‌های نقشه
    map.addControl(new NeshanMap.NavigationControl());
    map.addControl(new NeshanMap.GeolocateControl());

    // هندل کردن رویداد کلیک روی نقشه
    map.on('click', (e) => {
        const { lat, lng } = e.lngLat;
        
        // پاک کردن مارکرهای قبلی
        removeMarkers();
        
        // اضافه کردن مارکر جدید
        addMarker([lng, lat]);
        
        // ذخیره مختصات در فرم
        updateFormCoordinates(lat, lng);
    });

    return map;
};

// تابع اضافه کردن مارکر
const addMarker = (coordinates) => {
    new NeshanMap.Marker()
        .setLngLat(coordinates)
        .addTo(map);
};

// تابع به‌روزرسانی فرم
const updateFormCoordinates = (lat, lng) => {
    document.getElementById('latitude-input').value = lat;
    document.getElementById('longitude-input').value = lng;
};

// راه‌اندازی نقشه بعد از لود شدن صفحه
document.addEventListener('DOMContentLoaded', () => {
    const map = initMap();
    
    // اضافه کردن قابلیت جستجو
    const searchInput = document.getElementById('address-search');
    const searchButton = document.getElementById('search-btn');
    
    searchButton.addEventListener('click', () => {
        const query = searchInput.value;
        if (query) {
            searchLocation(query, map);
        }
    });
});

// تابع جستجوی مکان
const searchLocation = async (query, map) => {
    try {
        const response = await fetch(
            `https://api.neshan.org/v4/geocoding?address=${encodeURIComponent(query)}`,
            {
                headers: {
                    'Api-Key': mapConfig.mapKey
                }
            }
        );
        
        const data = await response.json();
        if (data.location) {
            const { x: lng, y: lat } = data.location;
            map.flyTo({
                center: [lng, lat],
                zoom: 15
            });
            addMarker([lng, lat]);
            updateFormCoordinates(lat, lng);
        }
    } catch (error) {
        console.error('خطا در جستجوی مکان:', error);
    }
};
