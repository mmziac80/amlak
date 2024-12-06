$(document).ready(function() {
    // تنظیمات تقویم شمسی برای تاریخ ورود و خروج
    $('#check-in-picker').persianDatepicker({
        format: 'YYYY/MM/DD',
        autoClose: true,
        minDate: new persianDate().unix(),
        onSelect: function() {
            $('#check-out-picker').prop('disabled', false);
            $('#check-out-picker').focus();
        }
    });

    $('#check-out-picker').persianDatepicker({
        format: 'YYYY/MM/DD',
        autoClose: true,
        minDate: new persianDate().unix(),
        disabled: true
    });

    // محاسبه قیمت کل
    function calculateTotalPrice() {
        const checkIn = $('#check-in-picker').val();
        const checkOut = $('#check-out-picker').val();
        
        if (checkIn && checkOut) {
            const checkInDate = new Date(checkIn.replace(/\//g, '-'));
            const checkOutDate = new Date(checkOut.replace(/\//g, '-'));
            const nights = (checkOutDate - checkInDate) / (1000 * 60 * 60 * 24);
            
            if (nights > 0) {
                const pricePerNight = parseInt($('.price').data('price'));
                const totalPrice = nights * pricePerNight;
                
                $('#nightsCount').text(nights + ' شب');
                $('#totalPrice').text(totalPrice.toLocaleString() + ' تومان');
                return true;
            }
        }
        
        $('#nightsCount').text('-');
        $('#totalPrice').text('-');
        return false;
    }

    // بررسی موجود بودن تاریخ‌ها
    function checkAvailability() {
        const propertyId = $('#bookingForm').data('property-id');
        const checkIn = $('#check-in-picker').val();
        const checkOut = $('#check-out-picker').val();

        if (checkIn && checkOut) {
            $.get(`/api/properties/${propertyId}/check-availability/`, {
                check_in: checkIn,
                check_out: checkOut
            })
            .done(function(response) {
                if (!response.available) {
                    alert('این تاریخ قبلاً رزرو شده است');
                    $('#check-in-picker').val('');
                    $('#check-out-picker').val('');
                }
            });
        }
    }

    // رویدادهای تغییر تاریخ
    $('#check-in-picker, #check-out-picker').on('change', function() {
        calculateTotalPrice();
        checkAvailability();
    });

    // ارسال فرم رزرو
    $('#bookingForm').on('submit', function(e) {
        e.preventDefault();
        
        if (!calculateTotalPrice()) {
            alert('لطفاً تاریخ ورود و خروج را انتخاب کنید');
            return;
        }

        const formData = {
            property: $(this).data('property-id'),
            check_in: $('#check-in-picker').val(),
            check_out: $('#check-out-picker').val(),
            guests_count: $('#id_guests_count').val()
        };

        $.ajax({
            url: '/api/bookings/create/',
            method: 'POST',
            data: formData,
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                window.location.href = `/bookings/${response.booking_id}/`;
            },
            error: function(xhr) {
                alert(xhr.responseJSON.message || 'خطا در ثبت رزرو');
            }
        });
    });
});
