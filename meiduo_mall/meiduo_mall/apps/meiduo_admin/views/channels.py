from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from meiduo_admin.serializers.categories import ChannelCategorySerializer
from meiduo_admin.serializers.channels import ChannelSerializer, ChannelTypeSerializer


class ChannelViewSet(ModelViewSet):
    # 指定视图所使用的序列化器
    serializer_class = ChannelSerializer
    # 指定视图所使用的查询集
    queryset = GoodsChannel.objects.all()

    # GET /meiduo_admin/goods/channels/ -> list
    # POST /meiduo_admin/goods/channels/ -> create

    # def list(self, request):
    #     qs = self.get_queryset()
    #     serializer = self.get_serializer(qs, many=True)
    #     return Response(serializer.data)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     serializer.save() # -> create
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)



    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save() # update
    #     return Response(serializer.data)

    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     instance.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


# GET /meiduo_admin/goods/channel_types/
# class ChannelTypesView(ListModelMixin, GenericAPIView):
class ChannelTypesView(ListAPIView):
    serializer_class = ChannelTypeSerializer
    queryset = GoodsChannelGroup.objects.all()

    # 注：关闭分页
    pagination_class = None

    # def get(self, request):
    #     """
    #     获取频道组的数据：
    #     1. 查询获取所有频道组的数据
    #     2. 将频道组数据序列化并返回
    #     """
    #     # 1. 查询获取所有频道组的数据
    #     channel_types = self.get_queryset()
    #
    #     # 2. 将频道组数据序列化并返回
    #     serializer = self.get_serializer(channel_types, many=True)
    #     return Response(serializer.data)

    # def get(self, request):
    #     return self.list(request)


# GET /meiduo_admin/goods/categories/
# class ChannelCategoryView(ListModelMixin, GenericAPIView):
class ChannelCategoryView(ListAPIView):
    serializer_class = ChannelCategorySerializer
    queryset = GoodsCategory.objects.filter(parent=None)

    # 注：关闭分页
    pagination_class = None

    # def get(self, request):
    #     return self.list(request)

    # def get(self, request):
    #     """
    #     获取一级分类的数据:
    #     1. 查询获取一级分类的数据
    #     2. 将一级分类数据序列化并返回
    #     """
    #     # 1. 查询获取一级分类的数据
    #     categories = self.get_queryset()
    #
    #     # 2. 将一级分类数据序列化并返回
    #     serializer = self.get_serializer(categories, many=True)
    #
    #     return Response(serializer.data)
