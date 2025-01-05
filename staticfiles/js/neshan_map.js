// Lazy loading imports
import(/* webpackChunkName: "neshan-styles" */ '@neshan-maps-platform/mapbox-gl/dist/NeshanMapboxGl.css');

const loadNeshanMap = () => import(/* webpackChunkName: "neshan-map" */ '@neshan-maps-platform/mapbox-gl');

document.addEventListener('DOMContentLoaded', function() {
    loadNeshanMap().then(module => {
        const nmp_mapboxgl = module.default;
        
        const mapElement = document.getElementById('detailPropertyMap');
        const locationInput = document.getElementById('location-input');

        console.group('مقداردهی اولیه نقشه');
        console.log('المان نقشه:', mapElement);
        console.log('ورودی موقعیت:', locationInput);

        let lat, lng;
        try {
            if (locationInput && locationInput.value) {
                const locationData = JSON.parse(locationInput.value);
                lat = locationData.lat;
                lng = locationData.lng;
                console.log('مختصات از ورودی موقعیت:', { lat, lng });
            } else {
                lat = parseFloat(mapElement.dataset.lat) || 36.2972;
                lng = parseFloat(mapElement.dataset.lng) || 59.6067;
                console.log('مختصات از dataset یا مقادیر پیش‌فرض:', { lat, lng });
            }

            if (!isFinite(lat) || !isFinite(lng)) {
                throw new Error('مختصات نامعتبر');
            }

            console.log('مختصات نهایی:', { lat, lng });
        
        setTimeout(() => {
            // ایجاد نقشه
            const map = new nmp_mapboxgl.Map({
                mapType: nmp_mapboxgl.Map.mapTypes.neshanVector,
                container: 'detailPropertyMap',
                zoom: 14,
                pitch: 0,
                center: [lng, lat],
                minZoom: 2,
                maxZoom: 21,
                mapKey: "web.ea06affc328a4934995818fed7a98b78"
            });

            // مارکر اصلی ملک
            const propertyMarker = new nmp_mapboxgl.Marker({
                color: "#FF0000",
                draggable: false
            })
            .setLngLat([lng, lat])
            .addTo(map);

            // مارکر موقعیت فعلی (آبی)
            let currentLocationMarker = null;

            // تغییر حالت نقشه (روز/شب)
            document.getElementById('detail-style-toggle').addEventListener('click', () => {
                console.group('تغییر حالت نقشه');
                const currentType = map.getMapType();
                console.log('حالت فعلی نقشه:', currentType);
                
                if (currentType === nmp_mapboxgl.Map.mapTypes.neshanVector) {
                    map.setMapType(nmp_mapboxgl.Map.mapTypes.neshanVectorNight);
                    console.log('نقشه به حالت شب تغییر کرد');
                } else {
                    map.setMapType(nmp_mapboxgl.Map.mapTypes.neshanVector);
                    console.log('نقشه به حالت روز تغییر کرد');
                }
                console.groupEnd();
            });

            // دکمه موقعیت فعلی با مارکر آبی
            document.getElementById('detail-locate-btn').addEventListener('click', () => {
                console.group('موقعیت‌یابی کاربر');
                if (navigator.geolocation) {
                    console.log('درخواست دسترسی به موقعیت...');
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            const { longitude, latitude } = position.coords;
                            console.log('موقعیت دریافت شد:', { longitude, latitude });
                            
                            // حذف مارکر قبلی موقعیت فعلی
                            if (currentLocationMarker) {
                                currentLocationMarker.remove();
                            }
                            
                            // ایجاد مارکر جدید آبی
                            currentLocationMarker = new nmp_mapboxgl.Marker({
                                color: "#0066FF",
                                draggable: false
                            })
                            .setLngLat([longitude, latitude])
                            .addTo(map);

                            // انتقال نقشه به موقعیت جدید
                            map.flyTo({
                                center: [longitude, latitude],
                                zoom: 15
                            });
                            console.log('نقشه به موقعیت کاربر منتقل شد');
                        },
                        (error) => {
                            console.error('خطا در دریافت موقعیت:', error.message);
                        }
                    );
                } else {
                    console.warn('مرورگر از موقعیت‌یابی پشتیبانی نمی‌کند');
                }
                console.groupEnd();
            });

            console.log('نقشه با موفقیت ایجاد شد');
        }, 100);

  
    } catch (error) {
        console.error('خطا در ایجاد نقشه:', error);
        lat = 36.2972;
        lng = 59.6067;
    }
    console.groupEnd();
}).catch(error => {
    console.error('خطا در بارگذاری ماژول نقشه:', error);
});
});