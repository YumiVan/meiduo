from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class OrderListSerializer(serializers.ModelSerializer):
    """订单序列化器类"""
    create_time = serializers.DateTimeField(label='下单时间', format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = OrderInfo
        fields = ('order_id', 'create_time')


class OrderSKUSerializer(serializers.ModelSerializer):
    """SKU商品序列化器类"""
    class Meta:
        model = SKU
        fields = ('name', 'default_image')


class OrderGoodsSerializer(serializers.ModelSerializer):
    """订单商品序列化器类"""
    # 关联对象的嵌套序列化
    sku = OrderSKUSerializer(label='sku商品')

    class Meta:
        model = OrderGoods
        fields = ('sku', 'price', 'count')


class OrderDetailSerializer(serializers.ModelSerializer):
    """订单序列化器类"""
    # 关联对象的嵌套序列化
    skus = OrderGoodsSerializer(label='订单商品', many=True)

    create_time = serializers.DateTimeField(label='下单时间', format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = OrderInfo
        exclude = ('address', 'update_time')


class OrderStatusSerializer(serializers.ModelSerializer):
    """订单序列化器类"""
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'status')
        read_only_fields = ('order_id', )

    def validate_status(self, value):
        # 检验订单状态是否有效
        if value not in [1, 2, 3, 4, 5, 6]:
            return serializers.ValidationError('订单状态有误')

        return value
