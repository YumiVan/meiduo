from rest_framework import serializers

from goods.models import SPU, SpecificationOption, SPUSpecification


class SPUSimpleSerializer(serializers.ModelSerializer):
    """SPU序列化器类"""
    class Meta:
        model = SPU
        fields = ('id', 'name')



class SpecOptionSerializer(serializers.ModelSerializer):
    """规格选项序列化器类"""
    class Meta:
        model = SpecificationOption
        fields = ('id', 'value')


class SPUSpecSerializer(serializers.ModelSerializer):
    """SPU规格序列化器类"""
    # 关联对象嵌套序列化
    spu = serializers.StringRelatedField(label='SPU名称')

    spu_id = serializers.IntegerField(label='SPU ID')

    # 关联对象嵌套序列化
    options = SpecOptionSerializer(label='选项', many=True)

    class Meta:
        model = SPUSpecification
        exclude = ('create_time', 'update_time')