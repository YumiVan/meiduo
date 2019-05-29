from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_admin.serializers.users import AdminAuthSerializer


# POST /meiduo_admin/authrizations/
class AdminAuthView(APIView):

    def post(self, request, pk):
        """
        管理员登录：
        1. 获取参数并进行校验(参数完整性，用户名和密码正确)
        2. 服务器创建一个jwt token，保存登录用户身份信息
        3. 返回响应，登录成功
        """
        # 1. 获取参数并进行校验(参数完整性，用户名和密码正确)
        serializer = AdminAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. 服务器创建一个jwt token，保存登录用户身份信息(create)
        serializer.save()

        # 3. 返回响应，登录成功
        return Response(serializer.data, status=status.HTTP_201_CREATED)