document.addEventListener('DOMContentLoaded', function() {
    const splideOptions = {
        perPage: 3,
        gap: 40,
        pagination: false,
        arrows: true,
        autoplay: true,
        interval: 3000,
        type: 'loop',
        direction: 'rtl',
        breakpoints: {
            768: { perPage: 2 },
            576: { perPage: 1 }
        }
    };

    document.querySelectorAll('.splide').forEach(carousel => {
        new Splide(carousel, splideOptions).mount();
    });
});
