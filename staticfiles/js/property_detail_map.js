const propertyDetailMap = {
    mapKey: 'web.ea06affc328a4934995818fed7a98b78',
    
    init: function(location) {
        // ایجاد نقشه
        this.map = new nmp_mapboxgl.Map({
            mapType: nmp_mapboxgl.Map.mapTypes.neshanVector,
            container: 'property-detail-map',
            zoom: 14,
            center: [location.lng, location.lat],
            minZoom: 5,
            maxZoom: 18,
            trackResize: true,
            mapKey: this.mapKey,
            poi: true
        });

        // افزودن مارکر اصلی
        this.marker = new nmp_mapboxgl.Marker({
            color: this.getPropertyTypeColor(location.type)
        })
        .setLngLat([location.lng, location.lat])
        .setPopup(new nmp_mapboxgl.Popup().setHTML(`
            <div class="map-popup">
                <h5>${location.title}</h5>
                <p>${location.address}</p>
            </div>
        `))
        .addTo(this.map);

        // افزودن کنترل‌های نقشه
        this.map.addControl(new nmp_mapboxgl.NavigationControl());
        this.addShareControl();
        this.addRoutingControl();
    },

    getPropertyTypeColor: function(type) {
        const colors = {
            'sale': '#FF4136',
            'rent': '#0074D9',
            'daily': '#2ECC40'
        };
        return colors[type] || '#AAAAAA';
    },

    addShareControl: function() {
        const shareButton = document.createElement('button');
        shareButton.className = 'map-control-button';
        shareButton.innerHTML = '<i class="fas fa-share-alt"></i>';
        shareButton.onclick = () => {
            const location = this.marker.getLngLat();
            const mapUrl = `https://www.google.com/maps?q=${location.lat},${location.lng}`;
            
            if (navigator.share) {
                navigator.share({
                    title: 'موقعیت ملک',
                    url: mapUrl
                });
            } else {
                navigator.clipboard.writeText(mapUrl)
                    .then(() => alert('لینک موقعیت کپی شد'));
            }
        };
        this.map.getContainer().appendChild(shareButton);
    },

    addRoutingControl: function() {
        const routingButton = document.createElement('button');
        routingButton.className = 'map-control-button';
        routingButton.innerHTML = '<i class="fas fa-directions"></i>';
        routingButton.onclick = () => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(position => {
                    const destination = this.marker.getLngLat();
                    window.open(
                        `https://www.google.com/maps/dir/${position.coords.latitude},${position.coords.longitude}/${destination.lat},${destination.lng}`,
                        '_blank'
                    );
                });
            }
        };
        this.map.getContainer().appendChild(routingButton);
    }
};
