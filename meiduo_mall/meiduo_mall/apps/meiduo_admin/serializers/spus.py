from rest_framework import serializers

from goods.models import SPU


class SPUSimpleSerializer(serializers.ModelSerializer):
    """SPU序列化器类"""
    class Meta:
        model = SPU
        fields = ('id', 'name')