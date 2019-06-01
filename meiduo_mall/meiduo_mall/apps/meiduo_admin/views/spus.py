from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser

from goods.models import SPU
from meiduo_admin.serializers.spus import SPUSimpleSerializer


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
