from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination
)
from rest_framework.response import Response
from collections import OrderedDict

class StandardResultsSetPagination(PageNumberPagination):
    """صفحه‌بندی استاندارد با شماره صفحه"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('current_page', self.page.number),
            ('total_pages', self.page.paginator.num_pages),
            ('results', data)
        ]))

class PaymentLimitOffsetPagination(LimitOffsetPagination):
    """صفحه‌بندی با محدودیت و آفست"""
    default_limit = 20
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('current_offset', self.offset),
            ('results', data)
        ]))

class PaymentCursorPagination(CursorPagination):
    """صفحه‌بندی با نشانگر برای کارایی بالا"""
    page_size = 20
    ordering = '-created_at'
    cursor_query_param = 'cursor'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

class TransactionPagination(StandardResultsSetPagination):
    """صفحه‌بندی تراکنش‌ها"""
    page_size = 15

class RefundRequestPagination(StandardResultsSetPagination):
    """صفحه‌بندی درخواست‌های استرداد"""
    page_size = 10

class PaymentReportPagination(StandardResultsSetPagination):
    """صفحه‌بندی گزارش‌های پرداخت"""
    page_size = 30
