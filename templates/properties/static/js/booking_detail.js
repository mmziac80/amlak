
$(document).ready(function() {
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
