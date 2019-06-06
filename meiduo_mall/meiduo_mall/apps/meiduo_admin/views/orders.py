from rest_framework.decorators import action
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser

from meiduo_admin.serializers.orders import OrderListSerializer, OrderDetailSerializer, OrderStatusSerializer
from orders.models import OrderInfo


class OrdersViewSet(UpdateModelMixin, ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # 获取keyword
        keyword = self.request.query_params.get('keyword')

        if keyword:
            # 查询订单中sku商品名称中函数keyword
            orders = OrderInfo.objects.filter(skus__sku__name__contains=keyword)
        else:
            # 获取所有的订单数据
            orders = OrderInfo.objects.all()

        return orders

    # 指定视图所使用的序列化器类
    # serializer_class = OrderListSerializer

    # 视图集对象action属性
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        else:
            # status操作
            return OrderStatusSerializer

    # GET /meiduo_admin/orders/ -> list
    # GET /meiduo_admin/orders/(?P<pk>\d+) -> retrieve
    # PUT /meiduo_admin/orders/(?P<pk>\d+)/status/ -> status

    # def list(self, request):
    #     qs = self.get_queryset()
    #     serializer = self.get_serializer(qs, many=True)
    #     return Response(serializer.data)

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        """
        修改指定订单的订单状态:
        1. 获取指定订单
        2. 获取status并进行校验(status必传，status是否合法)
        3. 修改指定订单的状态
        4. 返回应答
        """
        # # 1. 获取指定订单
        # order = self.get_object()
        #
        # # 2. 获取status并进行校验(status必传，status是否合法)
        # serializer = self.get_serializer(order, data=request.data)
        # serializer.is_valid(raise_exception=True)
        #
        # # 3. 修改指定订单的状态
        # serializer.save() # -> update
        #
        # # 4. 返回应答
        # return Response(serializer.data)

        return self.update(request, pk)
