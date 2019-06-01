from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from goods.models import GoodsVisitCount
from meiduo_admin.serializers.statistical import GoodsVisitCountSerializer
from users.models import User


# GET /meiduo_admin/statistical/total_count/
class UserTotalCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取网站总用户数：
        1. 统计网站总用户数量
        2. 返回响应
        """
        # 1. 统计网站总用户数量
        count = User.objects.count()

        # 2. 返回响应
        now_date = timezone.now() # 年-月-日 时:分:秒

        response_data = {
            # 年-月-日
            'date': now_date.date(),
            'count': count
        }

        return Response(response_data)


# GET /meiduo_admin/statistical/day_increment/
class UserDayIncrementView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取日新增用户数量：
        1. 统计网站日新增用户数量
        2. 返回响应
        """
        # 1. 统计网站日新增用户数量
        # 年-月-日 时:分:秒
        now_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = User.objects.filter(date_joined__gte=now_date).count()

        # 2. 返回响应
        response_data = {
            # 年-月-日
            'date': now_date.date(),
            'count': count
        }

        return Response(response_data)


# GET /meiduo_admin/statistical/day_active/
class UserDayActiveView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取日活跃用户数量:
        1. 统计网站当日活跃用户数量
        2. 返回响应
        """
        # 1. 统计网站当日活跃用户数量
        now_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = User.objects.filter(last_login__gte=now_date).count()

        # 2. 返回响应
        response_data = {
            # 年-月-日
            'date': now_date.date(),
            'count': count
        }

        return Response(response_data)


# GET /meiduo_admin/statistical/day_orders/
class UserDayOrderView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取日下单用户数量:
        1. 统计网站日下单用户数量
        2. 返回响应
        """
        # 1. 统计网站日下单用户数量
        now_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = User.objects.filter(orders__create_time__gte=now_date).count()

        # 2. 返回响应
        response_data = {
            # 年-月-日
            'date': now_date.date(),
            'count': count
        }

        return Response(response_data)


# GET /meiduo_admin/statistical/month_increment/
class UserMonthIncrementView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取网站近30天每日新增用户数量:
        1. 统计近30天网站每日新增用户数量
        2. 返回响应
        """
        # 1. 统计近30天网站每日新增用户数量
        now_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # 起始日期
        begin_date = now_date - timezone.timedelta(days=29)

        # 统计数量列表
        count_list = []

        for i in range(30): # 0-29
            # 当天日期
            cur_date = begin_date + timezone.timedelta(days=i)
            # 次日日期
            next_date = cur_date + timezone.timedelta(days=1)

            # 统计当天网站新增用户的数量
            count = User.objects.filter(date_joined__gte=cur_date, date_joined__lt=next_date).count()

            # 保存数据
            count_list.append({
                'date': cur_date.date(),
                'count': count
            })

        # 2. 返回响应
        return Response(count_list)



# GET /meiduo_admin/statistical/goods_day_views/
class GoodsDayViewsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取日分类商品访问量数据:
        1. 获取当天日分类商品访问量数据
        2. 将数据序列化并返回
        """
        # 1. 获取当天日分类商品访问量数据
        now_date = timezone.now().date() # '年-月-日'
        goods_visits = GoodsVisitCount.objects.filter(date=now_date)

        # 2. 将数据序列化并返回
        serializer = GoodsVisitCountSerializer(goods_visits, many=True)
        return Response(serializer.data)