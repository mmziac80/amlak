
import '@neshan-maps-platform/mapbox-gl/dist/NeshanMapboxGl.css';
import nmp_mapboxgl from '@neshan-maps-platform/mapbox-gl';

// تنظیمات API های نشان
const NESHAN_CONFIG = {
    MAP_KEY: "web.ea06affc328a4934995818fed7a98b78",
    SERVICE_KEY: 'service.90a4f40483534b1a987d3d5761f08a29',
    BASE_URL: 'https://api.neshan.org/v1'
};

// کلاس سرویس‌های نشان
class NeshanServices {
    static async searchAddress(term, lat = 36.2972, lng = 59.6067) {
        const url = `${NESHAN_CONFIG.BASE_URL}/search?term=${term}&lat=${lat}&lng=${lng}`;
        return await this.fetchNeshanAPI(url);
    }

    static async reverseGeocode(lat, lng) {
        const url = `${NESHAN_CONFIG.BASE_URL}/reverse?lat=${lat}&lng=${lng}`;
        return await this.fetchNeshanAPI(url);
    }

    static async getDistanceMatrix(origins, destinations) {
        const url = `${NESHAN_CONFIG.BASE_URL}/distance-matrix`;
        return await this.fetchNeshanAPI(url, {
            method: 'POST',
            body: JSON.stringify({ origins, destinations })
        });
    }

    static async getRoute(origin, destination, type = 'car') {
        const url = `${NESHAN_CONFIG.BASE_URL}/routing?origin=${origin.join(',')}&destination=${destination.join(',')}&type=${type}`;
        return await this.fetchNeshanAPI(url);
    }

    static async fetchNeshanAPI(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Api-Key': NESHAN_CONFIG.SERVICE_KEY
            }
        };
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            return await response.json();
        } catch (error) {
            console.error('Neshan API Error:', error);
            throw error;
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const mapElement = document.getElementById('propertyMap');
    const latInput = document.getElementById('latitude-input');
    const lngInput = document.getElementById('longitude-input');
    const locationInput = document.getElementById('location-input');
    const searchInput = document.getElementById('address-search');
    const searchBtn = document.getElementById('search-btn');

    // ایجاد نقشه
    const map = new nmp_mapboxgl.Map({
        mapType: nmp_mapboxgl.Map.mapTypes.neshanVector,
        container: mapElement,
        zoom: parseInt(mapElement.dataset.zoom || '14'),
        center: [
            parseFloat(mapElement.dataset.defaultLng || '59.6067'),
            parseFloat(mapElement.dataset.defaultLat || '36.2972')
        ],
        mapKey: NESHAN_CONFIG.MAP_KEY,
        poi: true,
        traffic: false
    });

    // تنظیم مارکر
    const marker = new nmp_mapboxgl.Marker({
        draggable: true,
        color: "#FF0000"
    });

    // نمایش موقعیت اولیه
    if (latInput.value && lngInput.value) {
        const lat = parseFloat(latInput.value);
        const lng = parseFloat(lngInput.value);
        marker.setLngLat([lng, lat]).addTo(map);
        map.flyTo({ center: [lng, lat] });
        
        // دریافت آدرس موقعیت اولیه
        NeshanServices.reverseGeocode(lat, lng)
            .then(data => {
                if (data.status === 'OK') {
                    searchInput.value = data.formatted_address;
                }
            });
    }

    // رویداد کلیک روی نقشه
    map.on('click', async (e) => {
        const { lng, lat } = e.lngLat;
        updateInputs(lng, lat);
        
        // دریافت آدرس محل کلیک شده
        try {
            const data = await NeshanServices.reverseGeocode(lat, lng);
            if (data.status === 'OK') {
                searchInput.value = data.formatted_address;
            }
        } catch (error) {
            console.error('خطا در دریافت آدرس:', error);
        }
    });

    // رویداد جابجایی مارکر
    marker.on('dragend', async () => {
        const { lng, lat } = marker.getLngLat();
        updateInputs(lng, lat);
        
        // دریافت آدرس محل جدید مارکر
        try {
            const data = await NeshanServices.reverseGeocode(lat, lng);
            if (data.status === 'OK') {
                searchInput.value = data.formatted_address;
            }
        } catch (error) {
            console.error('خطا در دریافت آدرس:', error);
        }
    });

    // تابع به‌روزرسانی ورودی‌ها
    function updateInputs(lng, lat) {
        if (!isFinite(lng) || !isFinite(lat)) {
            console.error('مختصات نامعتبر:', { lng, lat });
            return;
        }

        const formattedLat = parseFloat(lat.toFixed(6));
        const formattedLng = parseFloat(lng.toFixed(6));

        latInput.value = formattedLat;
        lngInput.value = formattedLng;
        locationInput.value = JSON.stringify({ lat: formattedLat, lng: formattedLng });

        marker.setLngLat([formattedLng, formattedLat]).addTo(map);
        
        // ارسال رویداد تغییر موقعیت
        const event = new CustomEvent('locationSelected', {
            detail: { lat: formattedLat, lng: formattedLng }
        });
        document.dispatchEvent(event);
    }

    // جستجوی آدرس
    searchBtn.addEventListener('click', async () => {
        const query = searchInput.value.trim();
        if (!query) return;

        searchInput.disabled = true;
        searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            const data = await NeshanServices.searchAddress(query);
            if (data.status === 'OK' && data.items.length > 0) {
                const location = data.items[0].location;
                updateInputs(location.x, location.y);
                map.flyTo({
                    center: [location.x, location.y],
                    zoom: 15
                });
            }
        } catch (error) {
            console.error('خطا در جستجوی آدرس:', error);
        } finally {
            searchInput.disabled = false;
            searchBtn.innerHTML = '<i class="fas fa-search"></i> جستجو';
        }
    });

    // تغییر حالت نقشه
    document.getElementById('style-toggle').addEventListener('click', () => {
        const button = document.getElementById('style-toggle');
        if (map.getMapType() === nmp_mapboxgl.Map.mapTypes.neshanVector) {
            map.setMapType(nmp_mapboxgl.Map.mapTypes.neshanVectorNight);
            button.innerHTML = '<i class="fas fa-sun"></i>';
            button.title = 'تغییر به حالت روز';
        } else {
            map.setMapType(nmp_mapboxgl.Map.mapTypes.neshanVector);
            button.innerHTML = '<i class="fas fa-moon"></i>';
            button.title = 'تغییر به حالت شب';
        }
    });

    // دکمه موقعیت فعلی
    document.getElementById('locate-btn').addEventListener('click', () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(async (position) => {
                const { longitude, latitude } = position.coords;
                updateInputs(longitude, latitude);
                map.flyTo({ center: [longitude, latitude], zoom: 15 });
                
                // دریافت آدرس موقعیت فعلی
                try {
                    const data = await NeshanServices.reverseGeocode(latitude, longitude);
                    if (data.status === 'OK') {
                        searchInput.value = data.formatted_address;
                    }
                } catch (error) {
                    console.error('خطا در دریافت آدرس:', error);
                }
            });
        }
    });
});
