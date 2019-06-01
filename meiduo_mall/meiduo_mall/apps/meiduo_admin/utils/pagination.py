# 自定DRF框架分页类
from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultPagination(PageNumberPagination):
    # 默认页容量
    page_size = 1
    # 获取分页数据时，`页容量`参数的名称
    page_size_query_param = 'pagesize'
    # 最大页容量
    max_page_size = 20

    def get_paginated_response(self, data):
        """分页之后的响应数据格式"""
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('lists', data),
            ('page', self.page.number),
            ('pages', self.page.paginator.num_pages),
            ('pagesize', self.get_page_size(self.request))
        ]))

