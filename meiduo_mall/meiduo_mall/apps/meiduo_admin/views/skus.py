from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SKUImage, SKU, GoodsCategory
from meiduo_admin.serializers.skus import SKUImageSerializer, SKUSimpleSerializer, SKUSerializer, SKUCategorySerializer


class SKUImageViewSet(ModelViewSet):
    """SKU图片视图集"""
    permission_classes = [IsAdminUser]
    # 指定视图所使用的查询集
    queryset = SKUImage.objects.all()
    # 指定视图所使用的序列化器类
    serializer_class = SKUImageSerializer

    # GET /meiduo_admin/skus/images/ -> list
    # POST /meiduo_admin/skus/images/ -> create
    # GET /meiduo_admin/skus/images/(?P<pk>\d+)/ -> retrieve
    # PUT /meiduo_admin/skus/images/(?P<pk>\d+)/ -> update
    # DELETE /meiduo_admin/skus/images/(?P<pk>\d+)/ -> destroy

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


# GET /meiduo_admin/skus/simple/
class SKUSimpleView(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = SKU.objects.all()
    serializer_class = SKUSimpleSerializer

    # 注：关闭分页
    pagination_class = None

    # def get(self, request):
    #     # return self.list(request)
    #     qs = self.get_queryset()
    #     serializer = self.get_serializer(qs, many=True)
    #     return Response(serializer.data)


class SKUViewSet(ModelViewSet):
    """SKU视图集"""
    permission_classes = [IsAdminUser]
    # 指定视图所使用的序列化器类
    serializer_class = SKUSerializer

    # 重写GenericAPIView中get_queryset
    def get_queryset(self):
        # 获取keyword
        keyword = self.request.query_params.get('keyword')

        if keyword:
            # |
            skus = SKU.objects.filter(Q(name__contains=keyword) |
                                      Q(caption__contains=keyword))
        else:
            skus = SKU.objects.all()

        return skus

    # GET /meiduo_admin/skus/ -> list

    # def list(self, request):
    #     qs = self.get_queryset()
    #     serializer = self.get_serializer(qs, many=True)
    #     return Response(serializer.data)

# GET /meiduo_admin/skus/categories/
class SKUCategoriesView(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = GoodsCategory.objects.filter(subs=None)

    serializer_class = SKUCategorySerializer

    # 注：关闭分页
    pagination_class = None

    # def get(self, request):
    #     # return self.list(request)
    #     qs = self.get_queryset()
    #     serializer = self.get_serializer(qs, many=True)
    #     return Response(serializer.data)

