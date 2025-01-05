
$(document).ready(function() {
    // تبدیل اعداد به فرمت فارسی با کاما
    function formatNumber(num) {
        return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
    }

    // تبدیل تاریخ میلادی به شمسی
    function toJalali(date) {
        return new persianDate(new Date(date)).format('YYYY/MM/DD HH:mm');
    }

    // اعمال فرمت فارسی به اعداد
    $('.amount').each(function() {
        const amount = $(this).text();
        $(this).text(formatNumber(amount));
    });

    // اعمال فرمت شمسی به تاریخ‌ها 
    $('.date').each(function() {
        const date = $(this).data('date');
        $(this).text(toJalali(date));
    });

    // فیلتر کردن پرداخت‌ها
    $('#status-filter').on('change', function() {
        const status = $(this).val();
        if(status === 'all') {
            $('tbody tr').show();
        } else {
            $('tbody tr').hide();
            $(`tbody tr[data-status="${status}"]`).show();
        }
    });

    // مرتب‌سازی جدول
    $('.sortable').on('click', function() {
        const column = $(this).data('column');
        const order = $(this).hasClass('asc') ? 'desc' : 'asc';
        
        // حذف کلاس‌های مرتب‌سازی قبلی
        $('.sortable').removeClass('asc desc');
        $(this).addClass(order);

        // مرتب‌سازی ردیف‌ها
        const rows = $('tbody tr').get();
        rows.sort(function(a, b) {
            const A = $(a).children(`td[data-${column}]`).data(column);
            const B = $(b).children(`td[data-${column}]`).data(column);
            
            if(order === 'asc') {
                return A > B ? 1 : -1;
            } else {
                return A < B ? 1 : -1;
            }
        });

        $.each(rows, function(index, row) {
            $('tbody').append(row);
        });
    });
});
