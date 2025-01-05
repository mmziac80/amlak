$(document).ready(function() {
    // اضافه کردن تنظیمات تقویم
    if ($.fn.persianDatepicker) {
        $('.datepicker').persianDatepicker({
            format: 'YYYY/MM/DD',
            initialValue: false,
            autoClose: true,
            persianDigit: true
        });
    }

    // بهبود کد فرم قبلی
    $('#visitForm').on('submit', function(e) {
        e.preventDefault();
        
        // اعتبارسنجی قبل از ارسال
        const dateValue = $('.datepicker').val();
        const visitTime = $('input[name="visit_time"]').val();
        
        if (!dateValue || !visitTime) {
            alert('لطفاً تاریخ و ساعت بازدید را وارد کنید');
            return;
        }

        $.ajax({
            url: $(this).attr('action'),
            method: 'POST',
            data: $(this).serialize(),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                $('#visitModal').modal('hide');
                alert(response.message);
            },
            error: function(xhr) {
                alert('خطا در ثبت درخواست');
            }
        });
    });

    // اضافه کردن handler برای دکمه تقویم
    $('#datepicker-trigger').on('click', function() {
        $('.datepicker').persianDatepicker('show');
    });
});
