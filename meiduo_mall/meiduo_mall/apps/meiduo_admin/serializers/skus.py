from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import APIException

from goods.models import SKUImage, SKU, SKUSpecification, GoodsCategory, SPU, SpecificationOption
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
    spec_id = serializers.IntegerField(label='规格id')
    option_id = serializers.IntegerField(label='选项id')

    class Meta:
        model = SKUSpecification
        fields = ('spec_id', 'option_id')
        # read_only


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

    def validate(self, attrs):
        # 获取category_id
        category_id = attrs['category_id']

        try:
            category = GoodsCategory.objects.get(id=category_id, subs=None)
        except GoodsCategory.DoesNotExist:
            raise serializers.ValidationError('第三级分类不存在')

        # 获取spu_id
        spu_id = attrs['spu_id']

        try:
            spu = SPU.objects.get(id=spu_id)
        except SPU.DoesNotExist:
            raise serializers.ValidationError('SPU不存在')

        # 检验category_id和spu的category3_id是否一致
        if category_id != spu.category3_id:
            raise serializers.ValidationError('第三级分类数据有误')

        # 检验spu的规格数据是否完整
        spu_specs = spu.specs.all() # 获取和spu关联的规格数据
        spu_specs_count = spu_specs.count()

        specs = attrs['specs']

        if spu_specs_count != len(specs):
            raise serializers.ValidationError('SKU规格数据不完整')

        # 检验spu的规格数据和传递的规格数据是否一致
        spu_specs_ids = [spec.id for spec in spu_specs] # [11, 12, 13]
        specs_ids = [spec.get('spec_id') for spec in specs] # [11, 13, 12]
        spu_specs_ids.sort()
        specs_ids.sort()
        if spu_specs_ids != specs_ids:
            raise serializers.ValidationError('SKU规格数据有误')

        # 检验传递的每个规格的选项在spu对应的规格下是否存在
        for spec in specs:
            # 获取spec_id, option_id
            spec_id = spec.get('spec_id')
            option_id = spec.get('option_id') # 3

            # 获取spec_id对应规格下面选项
            options = SpecificationOption.objects.filter(spec_id=spec_id)
            options_ids = [option.id for option in options] # [1, 2, 3]

            if option_id not in options_ids:
                raise serializers.ValidationError('规格选项数据有误')

        return attrs

    # ModelSerializer->create->SKU.objects.create()
    def create(self, validated_data):
        specs = validated_data.pop('specs')

        with transaction.atomic():
            # with语句块下的代码，凡是涉及到数据库操作的，都会放在同一个事务中
            # 添加sku商品的数据
            sku = super().create(validated_data)

            # 添加sku商品规格选项数据
            for spec in specs:
                # 获取spec_id和option_id
                spec_id = spec.get('spec_id')
                option_id = spec.get('option_id')

                SKUSpecification.objects.create(
                    sku=sku,
                    spec_id=spec_id,
                    option_id=option_id
                )

        return sku

    def update(self, instance, validated_data):
        """
        instance: sku商品对象
        """
        specs = validated_data.pop('specs')

        with transaction.atomic():
            # 更新sku商品的数据
            super().update(instance, validated_data)

            # 更新sku商品的规格选项数据
            sku_specs = instance.specs.all()

            sku_specs_li = [{
                                'spec_id': spec.spec_id,
                                'option_id': spec.option_id
                            }
                            for spec in sku_specs]

            if specs != sku_specs_li:
                # 删除sku原有的规格选项数据
                sku_specs.delete()

                # 添加sku商品规格选项数据
                for spec in specs:
                    # 获取spec_id和option_id
                    spec_id = spec.get('spec_id')
                    option_id = spec.get('option_id')

                    SKUSpecification.objects.create(
                        sku=instance,
                        spec_id=spec_id,
                        option_id=option_id
                    )

        return instance








class SKUCategorySerializer(serializers.ModelSerializer):
    """分类序列化器类"""
    class Meta:
        model = GoodsCategory
        fields = ('id', 'name')

