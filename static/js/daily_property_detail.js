
$(document).ready(function() {
    // دریافت اطلاعات از data attributes
    const form = $('#bookingForm');
    const minStay = parseInt(form.data('min-stay'));
    const maxGuests = parseInt(form.data('max-guests'));
    const dailyPrice = parseInt(form.data('daily-price'));
    const extraPersonFee = parseInt(form.data('extra-person-fee'));

    // تغییر تابع محاسبه قیمت کل
    function calculateTotalPrice() {
        const checkIn = $('#check-in-picker').val();
        const checkOut = $('#check-out-picker').val();
        const guestsCount = parseInt($('#id_guests_count').val());
        
        if (checkIn && checkOut) {
            const checkInDate = new Date(checkIn.replace(/\//g, '-'));
            const checkOutDate = new Date(checkOut.replace(/\//g, '-'));
            const nights = (checkOutDate - checkInDate) / (1000 * 60 * 60 * 24);
            
            // بررسی حداقل مدت اقامت
            if (nights < minStay) {
                alert(`حداقل مدت اقامت ${minStay} شب است`);
                $('#check-out-picker').val('');
                return false;
            }
            
            if (nights > 0) {
                // محاسبه قیمت پایه
                let totalPrice = nights * dailyPrice;
                
                // محاسبه هزینه نفرات اضافه
                if (guestsCount > 2 && extraPersonFee) {
                    totalPrice += (guestsCount - 2) * extraPersonFee * nights;
                }
                
                $('#nightsCount').text(nights + ' شب');
                $('#totalPrice').text(totalPrice.toLocaleString() + ' تومان');
                return true;
            }
        }
        
        $('#nightsCount').text('-');
        $('#totalPrice').text('-');
        return false;
    }

    // محدود کردن تعداد نفرات
    $('#id_guests_count').on('change', function() {
        const selectedGuests = parseInt($(this).val());
        if (selectedGuests > maxGuests) {
            alert(`حداکثر ظرفیت ${maxGuests} نفر است`);
            $(this).val(maxGuests);
        }
        calculateTotalPrice();
    });

    // اضافه کردن اعتبارسنجی به فرم
    $('#bookingForm').on('submit', function(e) {
        e.preventDefault();
        
        const checkIn = $('#check-in-picker').val();
        const checkOut = $('#check-out-picker').val();
        
        if (!checkIn || !checkOut) {
            alert('لطفاً تاریخ ورود و خروج را انتخاب کنید');
            return;
        }

        const nights = (new Date(checkOut) - new Date(checkIn)) / (1000 * 60 * 60 * 24);
        if (nights < minStay) {
            alert(`حداقل مدت اقامت ${minStay} شب است`);
            return;
        }

        const guestsCount = parseInt($('#id_guests_count').val());
        if (guestsCount > maxGuests) {
            alert(`حداکثر ظرفیت ${maxGuests} نفر است`);
            return;
        }

        // ادامه کد ارسال فرم
        const formData = {
            property: $(this).data('property-id'),
            check_in: checkIn,
            check_out: checkOut,
            guests_count: guestsCount
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

    // کد موجود برای تقویم و سایر توابع
    // ...

    // تبدیل اعداد به فرمت فارسی با کاما
    function formatNumber(num) {
        return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
    }

    // نمایش تاریخ‌ها به فرمت شمسی
    function convertToJalali(date) {
        return new persianDate(new Date(date)).format('YYYY/MM/DD');
    }

    // به‌روزرسانی وضعیت رزرو
    function updateBookingStatus() {
        $.get(`/api/bookings/${bookingId}/status/`, function(response) {
            const statusElement = $('.booking-status');
            statusElement.find('h6').text(`وضعیت رزرو: ${response.status_display}`);
            
            if (response.status === 'paid') {
                statusElement.removeClass().addClass('alert alert-success');
                statusElement.find('p').html(`
                    شماره پیگیری: ${response.payment_id}<br>
                    تاریخ پرداخت: ${convertToJalali(response.payment_date)}
                `);
            }
        });
    }

    // شروع فرآیند پرداخت
    window.startPayment = function() {
        $.ajax({
            url: `/api/bookings/${bookingId}/payment/`,
            method: 'POST',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.payment_url) {
                    window.location.href = response.payment_url;
                }
            },
            error: function(xhr) {
                alert('خطا در شروع فرآیند پرداخت');
            }
        });
    };

    // بررسی دوره‌ای وضعیت رزرو
    if ($('.booking-status').length) {
        setInterval(updateBookingStatus, 30000); // هر 30 ثانیه
    }

    // نمایش اولیه تاریخ‌ها به فرمت شمسی
    $('.booking-info .date').each(function() {
        const date = $(this).data('date');
        if (date) {
            $(this).text(convertToJalali(date));
        }
    });

    // نمایش اعداد با فرمت فارسی
    $('.booking-info .price').each(function() {
        const price = $(this).data('price');
        if (price) {
            $(this).text(formatNumber(price) + ' تومان');
        }
    });
});
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
