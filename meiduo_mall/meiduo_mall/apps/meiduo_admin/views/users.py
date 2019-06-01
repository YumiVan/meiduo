from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin

from meiduo_admin.serializers.users import AdminAuthSerializer, UserSerializer

# POST /meiduo_admin/authrizations/
# class AdminAuthView(CreateModelMixin, GenericAPIView):
from users.models import User


class AdminAuthView(CreateAPIView):
    # 指定视图所使用的序列化器类
    serializer_class = AdminAuthSerializer

    # def post(self, request):
    #     """
    #     管理员登录：
    #     1. 获取参数并进行校验(参数完整性，用户名和密码正确)
    #     2. 服务器创建一个jwt token，保存登录用户身份信息
    #     3. 返回响应，登录成功
    #     """
    #     # 1. 获取参数并进行校验(参数完整性，用户名和密码正确)
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # 2. 服务器创建一个jwt token，保存登录用户身份信息(create)
    #     serializer.save()
    #
    #     # 3. 返回响应，登录成功
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def post(self, request):
    #     return self.create(request)


# GET /meiduo_admin/users/?keyword=<关键字>
# class UserInfoView(ListModelMixin, GenericAPIView):
# class UserInfoView(ListModelMixin, CreateModelMixin, GenericAPIView):
# class UserInfoView(CreateModelMixin, ListAPIView):
class UserInfoView(ListCreateAPIView):
    # 指定视图所使用的序列化器类
    serializer_class = UserSerializer

    def get_queryset(self):
        """重写GenericAPIView中的get_queryset"""
        # self.request: 请求request对象
        keyword = self.request.query_params.get('keyword') # None

        if keyword:
            # 1.1 如果keyword不为空，根据用户名搜索普通用户
            users = User.objects.filter(username__contains=keyword, is_staff=False)
        else:
            # 1.2 否则，获取所有普通用户的数据
            users = User.objects.filter(is_staff=False)

        return users

    # def post(self, request):
    #     return self.create(request)

    # def post(self, request):
    #     """
    #     网站用户数据的新增:
    #     1. 获取参数并进行校验(参数完整性，手机号格式，手机号是否注册，邮箱格式)
    #     2. 创建并保存新用户的数据
    #     3. 将新用户数据序列化并返回
    #     """
    #     # 1. 获取参数并进行校验(参数完整性，手机号格式，手机号是否注册，邮箱格式)
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # 2. 创建并保存新用户的数据(调用create)
    #     serializer.save()
    #
    #     # 3. 将新用户数据序列化并返回
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def get(self, request):
    #     """
    #     self.request: 请求request对象
    #     网站用户数据的获取:
    #     1. 获取网站的普通用户的数据
    #         1.1 如果keyword不为空，根据用户名搜索普通用户
    #         1.2 否则，获取所有普通用户的数据
    #     2. 将用户的数据序列化并返回
    #     """
    #     # 1. 获取网站的普通用户的数据
    #     users = self.get_queryset()
    #
    #     # 2. 将用户的数据序列化并返回
    #     serializer = self.get_serializer(users, many=True)
    #     return Response(serializer.data)

    # def get(self, request):
    #     return self.list(request)






















