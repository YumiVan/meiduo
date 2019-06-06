from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser

from goods.models import SPU, SPUSpecification
from meiduo_admin.serializers.spus import SPUSimpleSerializer, SPUSpecSerializer


# GET /meiduo_admin/goods/simple/
class SPUSimpleView(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = SPU.objects.all()
    serializer_class = SPUSimpleSerializer

    # 注：关闭分页
    pagination_class = None

    # def get(self, request):
    #     # return self.list(request)
    #     qs = self.get_queryset()
    #     serializer = self.get_serializer(qs, many=True)
    #     return Response(serializer.data)


# GET /meiduo_admin/goods/(?P<pk>\d+)/specs/
# class SPUSpecView(ListModelMixin, GenericAPIView):
class SPUSpecView(ListAPIView):
    permission_classes = [IsAdminUser]
    # 指定序列化器类
    serializer_class = SPUSpecSerializer
    # 指定视图所使用的查询集
    # queryset = SPUSpecification.objects.filter(spu_id=pk)

    def get_queryset(self):
        # 获取从url地址中提取的pk参数
        pk = self.kwargs['pk']

        return SPUSpecification.objects.filter(spu_id=pk)

    # 注：关闭分类
    pagination_class = None

    # def get(self, request, pk):
    #     return self.list(request, pk)

    # def get(self, request, pk):
    #     """
    #     self.kwargs: 字典，保存从url地址中提取的所有命名参数
    #     获取SPU规格选项数据:
    #     1. 获取和spu对象关联的规格数据
    #     2. 将获取规格数据序列化并返回
    #     """
    #     # 1. 获取和spu对象关联的规格数据
    #     specs = self.get_queryset()
    #
    #     # 2. 将获取规格数据序列化并返回
    #     serializer = self.get_serializer(specs, many=True)
    #     return Response(serializer.data)
