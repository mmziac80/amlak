import { useState, useEffect } from 'react';
import { MapComponent } from "@neshan-maps-platform/mapbox-gl-react";
import '@neshan-maps-platform/mapbox-gl/dist/NeshanMapboxGl.css';
import './LocationPicker.css';
import nmp_mapboxgl from '@neshan-maps-platform/mapbox-gl';

const LocationPicker = ({ onLocationSelect, initialLocation = null, dealType = 'sale' }) => {
    const [map, setMap] = useState(null);
    const [marker, setMarker] = useState(null);
    const [currentLocation, setCurrentLocation] = useState(initialLocation);

    // مدیریت مارکر اولیه
    useEffect(() => {
        if (map && initialLocation) {
            // حذف مارکر قبلی اگر وجود داره
            if (marker) {
                marker.remove();
            }

            const popup = new nmp_mapboxgl.Popup({ offset: 25 })
                .setText('موقعیت فعلی');

            const newMarker = new nmp_mapboxgl.Marker({
                color: dealType === 'sale' ? '#FF4444' : dealType === 'rent' ? '#00F955' : '#9B59B6',
                draggable: true
            })
                .setLngLat([initialLocation.lng, initialLocation.lat])
                .setPopup(popup)
                .addTo(map);

            // اضافه کردن event listener برای drag
            newMarker.on('dragend', () => {
                const lngLat = newMarker.getLngLat();
                setCurrentLocation(lngLat);
                onLocationSelect(lngLat);
            });

            setMarker(newMarker);
            setCurrentLocation(initialLocation);
        }
    }, [map, initialLocation, dealType]);

    const handleMapClick = (e) => {
        if (!map) return;

        // حذف مارکر قبلی
        if (marker) {
            marker.remove();
        }

        const newLocation = {
            lng: e.lngLat.lng,
            lat: e.lngLat.lat
        };

        const popup = new nmp_mapboxgl.Popup({ offset: 25 })
            .setText('موقعیت انتخاب شده');

        const newMarker = new nmp_mapboxgl.Marker({
            color: dealType === 'sale' ? '#FF4444' : dealType === 'rent' ? '#00F955' : '#9B59B6',
            draggable: true
        })
            .setLngLat([newLocation.lng, newLocation.lat])
            .setPopup(popup)
            .addTo(map);

        // اضافه کردن event listener برای drag
        newMarker.on('dragend', () => {
            const lngLat = newMarker.getLngLat();
            setCurrentLocation(lngLat);
            onLocationSelect(lngLat);
        });

        setMarker(newMarker);
        setCurrentLocation(newLocation);
        onLocationSelect(newLocation);
    };
    
    

    return (
        <div className="relative w-full h-[400px] rounded-lg overflow-hidden">
            <MapComponent
                options={{
                    mapKey: "web.ea06affc328a4934995818fed7a98b78",
                    center: [59.6167, 36.2972], // مختصات مشهد
                    zoom: 13,
                    poi: true,
                    traffic: false
                }}
                mapSetter={(mapInstance) => {
                    console.log('Map instance created:', mapInstance);
                    setMap(mapInstance);
                    mapInstance.on('click', handleMapClick);
                    console.log('Click handler attached');
                }}
                
                className="w-full h-full"
            />
            <div className="absolute top-4 right-4 bg-white p-3 rounded-lg shadow-md text-sm">
                برای انتخاب موقعیت، روی نقشه کلیک کنید
            </div>

        </div>
    );
};

export default LocationPicker;
