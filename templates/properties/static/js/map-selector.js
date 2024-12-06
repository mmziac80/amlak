django.jQuery(function($) {
    const map = L.map('location-map', {
        center: [36.2972, 59.6067],
        zoom: 12
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
    }).addTo(map);

    let marker;

    map.on('click', function(e) {
        if (marker) {
            marker.remove();
        }
        marker = L.marker(e.latlng).addTo(map);
        $('#id_latitude').val(e.latlng.lat);
        $('#id_longitude').val(e.latlng.lng);
    });
});


