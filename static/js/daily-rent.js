$(document).ready(function() {
    // تنظیمات تقویم شمسی برای فیلتر جستجو
    $('#search-check-in').persianDatepicker({
        format: 'YYYY/MM/DD',
        autoClose: true,
        minDate: new persianDate().startOf('day').valueOf(),
        initialValue: false,
        onSelect: function() {
            const selectedDate = $('#search-check-in').persianDatepicker('getState').selected.unixDate;
            $('#search-check-out')
                .prop('disabled', false)
                .persianDatepicker('setMinDate', selectedDate)
                .persianDatepicker('show');
        }
    });

    $('#search-check-out').persianDatepicker({
        format: 'YYYY/MM/DD',
        autoClose: true,
        minDate: new persianDate().startOf('day').valueOf(),
        initialValue: false,
        disabled: true
    });

    // تنظیمات تقویم شمسی برای مودال رزرو
    $('#check-in-picker').persianDatepicker({
        format: 'YYYY/MM/DD',
        autoClose: true,
        minDate: new persianDate().startOf('day').valueOf(),
        initialValue: false,
        onSelect: function() {
            const selectedDate = $('#check-in-picker').persianDatepicker('getState').selected.unixDate;
            $('#check-out-picker')
                .prop('disabled', false)
                .persianDatepicker('setMinDate', selectedDate)
                .persianDatepicker('show');
            calculateTotalPrice();
        }
    });

    $('#check-out-picker').persianDatepicker({
        format: 'YYYY/MM/DD',
        autoClose: true,
        minDate: new persianDate().startOf('day').valueOf(),
        initialValue: false,
        disabled: true,
        onSelect: function() {
            calculateTotalPrice();
        }
    });

    // مدیریت مودال رزرو
    $('#bookingModal').on('show.bs.modal', function(event) {
        const button = $(event.relatedTarget);
        const propertyId = button.data('property-id');
        const price = button.data('price');
        const maxGuests = button.data('max-guests');

        $('#property-id').val(propertyId);
        $('#price-per-night').text(price.toLocaleString());
        $('#guests-count').attr('max', maxGuests);

        // ریست کردن فرم
        $('#booking-form')[0].reset();
        $('#check-in-picker').val('');
        $('#check-out-picker').val('').prop('disabled', true);
        $('#nights-count').text('0');
        $('#total-price').text('0');
        $('#booking-error').hide();
    });

    // محاسبه قیمت کل
    function calculateTotalPrice() {
        const checkIn = $('#check-in-picker').persianDatepicker('getState').selected.unixDate;
        const checkOut = $('#check-out-picker').persianDatepicker('getState').selected.unixDate;
        
        if (checkIn && checkOut && checkIn < checkOut) {
            const diffTime = Math.abs(checkOut - checkIn);
            const nights = Math.ceil(diffTime / (24 * 60 * 60));
            const price = parseInt($('#price-per-night').text().replace(/,/g, ''), 10);
            
            $('#nights-count').text(nights);
            $('#total-price').text((nights * price).toLocaleString());
        }
    }

    // ارسال فرم رزرو
    $('#booking-form').on('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            property: $('#property-id').val(),
            check_in: $('#check-in-picker').val(),
            check_out: $('#check-out-picker').val(),
            guests_count: $('#guests-count').val(),
            total_price: $('#total-price').text().replace(/,/g, '')
        };

        $.ajax({
            url: '/api/bookings/create/',
            method: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(response) {
                window.location.href = `/payments/${response.booking_id}/`;
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.message || 'خطا در ثبت رزرو';
                $('#booking-error').text(error).show();
            }
        });
    });

    // کنترل تعداد مهمان‌ها
    $('#guests-count').on('change', function() {
        const maxGuests = parseInt($(this).attr('max'), 10);
        const selectedGuests = parseInt($(this).val(), 10);

        if (selectedGuests > maxGuests) {
            $(this).val(maxGuests);
            $('#guests-error').text('تعداد مهمان‌ها نمی‌تواند بیشتر از ظرفیت اقامتگاه باشد').show();
        } else {
            $('#guests-error').hide();
        }
    });
});
