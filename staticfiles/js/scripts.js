$(document).ready(function() {
    // تنظیمات Select2 برای المان‌های با کلاس select2-enable
    $('.select2-enable').select2({
        theme: 'bootstrap-5',
        dir: "rtl",
        language: "fa",
        width: '100%'
    });

    // اسلایدر متراژ
    const areaSlider = document.getElementById('area-slider');
    if(areaSlider) {
        noUiSlider.create(areaSlider, {
            start: [0, 500],
            connect: true,
            direction: 'rtl',
            range: {
                'min': 0,
                'max': 500
            },
            format: {
                to: value => Math.round(value),
                from: value => value
            }
        });

        const minAreaInput = document.querySelector('[name="min_area"]');
        const maxAreaInput = document.querySelector('[name="max_area"]');
        const areaMinSpan = document.getElementById('area-min');
        const areaMaxSpan = document.getElementById('area-max');

        areaSlider.noUiSlider.on('update', function(values, handle) {
            const value = values[handle];
            if (handle) {
                maxAreaInput.value = value;
                areaMaxSpan.textContent = value + ' متر';
            } else {
                minAreaInput.value = value;
                areaMinSpan.textContent = value + ' متر';
            }
        });
    }

    // نمایش اسلایدر مناسب بر اساس نوع معامله
    const dealTypeSelect = document.querySelector('[name="deal_type"]');
    const salePriceSlider = document.getElementById('sale-price-slider');
    const rentPriceSlider = document.getElementById('rent-price-slider');
    
    function togglePriceSliders() {
        if (dealTypeSelect.value === 'sale') {
            salePriceSlider.style.display = 'block';
            rentPriceSlider.style.display = 'none';
        } else if (dealTypeSelect.value === 'rent') {
            salePriceSlider.style.display = 'none';
            rentPriceSlider.style.display = 'block';
        }
    }
    
    dealTypeSelect?.addEventListener('change', togglePriceSliders);
    togglePriceSliders();

    // تابع نقشه
    function initMap(latitude, longitude) {
        var map = L.map('map').setView([latitude, longitude], 15);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        L.marker([latitude, longitude]).addTo(map);
    }
});
