$(document).ready(function() {
    // اسلایدر قیمت پرداخت
    var paymentSlider = document.getElementById('payment-slider');
    if(paymentSlider) {
        noUiSlider.create(paymentSlider, {
            start: [0, 1000000000],
            connect: true,
            direction: 'rtl',
            range: {
                'min': 0,
                'max': 1000000000
            },
            format: {
                to: function (value) {
                    return Math.round(value).toLocaleString('fa-IR');
                },
                from: function (value) {
                    return value;
                }
            }
        });
    }

    // مدیریت فرم پرداخت
    $('#paymentForm').on('submit', function(e) {
        e.preventDefault();
        const amount = $('#amount').val();
        const gateway = $('#gateway').val();
        
        $.ajax({
            url: '/payments/init/',
            method: 'POST',
            data: {
                amount: amount,
                gateway: gateway
            },
            success: function(response) {
                window.location.href = response.payment_url;
            }
        });
    });

    // نمایش جزئیات پرداخت
    $('.payment-detail-btn').on('click', function() {
        const paymentId = $(this).data('payment-id');
        $.get(`/payments/detail/${paymentId}/`, function(data) {
            $('#paymentDetailModal .modal-body').html(data);
            $('#paymentDetailModal').modal('show');
        });
    });
});
