from rest_framework import serializers

from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory


# channel = GoodsChannel.objects.get(id=1)
# channel.category
# channel.category_id
# channel.group
# channel.group_id
class ChannelSerializer(serializers.ModelSerializer):
    """频道序列化器类"""
    # 关联对象嵌套序列化：将关联对象序列化为关联对象模型类__str__方法的返回值
    category = serializers.StringRelatedField(label='一级分类名称')
    group = serializers.StringRelatedField(label='频道组的名称')

    category_id = serializers.IntegerField(label='一级分类id')
    group_id = serializers.IntegerField(label='频道组id')

    class Meta:
        model = GoodsChannel
        fields = ('id', 'category', 'category_id', 'group', 'group_id', 'sequence', 'url')

    def validate_category_id(self, value):
        """一级分类是否存在"""
        try:
            category = GoodsCategory.objects.get(id=value, parent=None)
        except GoodsCategory.DoesNotExist:
            raise serializers.ValidationError('一级分类不存在')

        return value

    def validate_group_id(self, value):
        """频道组是否存在"""
        try:
            group = GoodsChannelGroup.objects.get(id=value)
        except GoodsChannelGroup.DoesNotExist:
            raise serializers.ValidationError('频道组不存在')

        return value


class ChannelTypeSerializer(serializers.ModelSerializer):
    """频道组序列化器类"""
    class Meta:
        model = GoodsChannelGroup
        fields = ('id', 'name')