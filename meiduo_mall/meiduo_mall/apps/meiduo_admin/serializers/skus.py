from rest_framework import serializers
from rest_framework.exceptions import APIException

from goods.models import SKUImage, SKU, SKUSpecification
from meiduo_mall.utils.fastdfs.fdfs_storage import FastDFSStorage


# sku_image = SKUImage.objects.get(id=1)
# sku_image.sku
class SKUImageSerializer(serializers.ModelSerializer):
    """SKU图片序列化器类"""
    sku_id = serializers.IntegerField(label='SKU商品id')

    # 关联对象嵌套序列化
    sku = serializers.StringRelatedField(label='SKU商品名称')

    class Meta:
        model = SKUImage
        exclude = ('create_time', 'update_time')

    def validate_sku_id(self, value):
        # sku_id对应的sku商品是否存在
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('SKU商品不存在')

        # return value
        # 注意：返回的是查到sku对象，之后在validated_data中
        # 获取的sku_id就是这里返回sku对象
        return sku

    # ModelSerializer->update
    def update(self, instance, validated_data):
        # 获取上传文件对象
        file = validated_data['image']

        # 获取sku对象
        sku = validated_data['sku_id']

        # 上传图片到fdfs系统
        fdfs = FastDFSStorage()
        try:
            file_id = fdfs.save(file.name, file)
        except Exception:
            # 上传文件失败
            raise APIException('上传文件失败')

        # 修改SKU图片数据
        instance.sku = sku
        instance.image = file_id
        instance.save()

        return instance

    # ModelSerializer->create->SKUImage.objects.create()
    def create(self, validated_data):
        # 获取上传文件对象
        file = validated_data['image']

        # 获取sku对象
        sku = validated_data['sku_id']

        # 上传图片到fdfs系统
        fdfs = FastDFSStorage()
        try:
            file_id = fdfs.save(file.name, file)
        except Exception:
            # 上传文件失败
            raise APIException('上传文件失败')

        # 保存上传图片记录
        sku_image = SKUImage.objects.create(
            sku=sku,
            # sku_id=sku.id,
            image=file_id
        )

        # sku商品的默认图片设置
        if not sku.default_image:
            sku.default_image = sku_image.image.url
            sku.save()

        return sku_image


class SKUSimpleSerializer(serializers.ModelSerializer):
    """SKU商品序列化器类"""
    class Meta:
        model = SKU
        fields = ('id', 'name')


class SKUSpecSerializer(serializers.ModelSerializer):
    """SKU规格选项序列化器类"""
    class Meta:
        model = SKUSpecification
        fields = ('spec_id', 'option_id')


# sku = SKU.objects.get(id=1)
# sku.spu -> 获取和sku关联的spu数据
# sku.category -> 获取和sku关联的第三级分类数据
# sku.specs -> 获取和sku关联的规格选项数据
class SKUSerializer(serializers.ModelSerializer):
    """SKU商品序列化器类"""
    # 关联对象嵌套序列化
    spu = serializers.StringRelatedField(label='SPU名称')
    category = serializers.StringRelatedField(label='第三级分类')

    spu_id = serializers.IntegerField(label='SPU ID')
    category_id = serializers.IntegerField(label='第三级分类id')

    # 关联对象嵌套序列化：使用指定的序列化器将关联对象进行序列化
    specs = SKUSpecSerializer(label='SKU规格选项数据', many=True)

    class Meta:
        model = SKU
        exclude = ('default_image', 'create_time', 'update_time')
