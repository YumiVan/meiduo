from django.shortcuts import render, redirect,reverse
from django.views import View
from django import http
from django.contrib.auth import login, logout, authenticate,mixins
from django.db import DatabaseError
from meiduo_mall.utils.response_code import RETCODE
from django_redis import get_redis_connection
from .models import User
import logging
import re

logger = logging.getLogger('django')  # 创建日志输出器


# Create your views here.
class RegisterView(View):
    '''注册'''

    def get(self, request):
        '''提供注册界面'''
        return render(request, 'register.html')

    def post(self, request):
        '''用户注册功能'''
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code = request.POST.get('sms_code')
        allow = request.POST.get('allow')  # "on"  None

        if all([username, password, password2, mobile, sms_code, allow]) is False:
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入8-20个字符的用户名')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        if password2 != password:
            return http.HttpResponseForbidden('两次密码不一致')
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号格式')
        # 短信验证码校验后期补充
        redis_coon = get_redis_connection('verify_code')
        sms_code_server = redis_coon.get('sms_%s' % mobile)  # 获取redis中的短信验证码

        if sms_code_server is None or sms_code != sms_code_server.decode():
            return http.HttpResponseForbidden('短信验证码有误')

        # 创建一个user
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                mobile=mobile
            )
        except DatabaseError as e:
            logger.error(e)
            return render(request, 'register.html', {'register_errmsg': '用户注册失败'})

        # 状态保持
        login(request, user)  #
        # 注册成功重定向到首页
        response = redirect('/')  # 创建响应对象
        response.set_cookie('username', user.username, max_age=60 * 60)
        # 响应结果重定向到首页
        return response


class UsernameCountView(View):
    '''判断用户名已注册'''

    def get(self, request, username):
        '''查询当前用户名的个数 要么0要么1'''
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'count': count, 'code': RETCODE.OK, 'errmsg': 'OK'})


class MobileCountView(View):
    '''判断手机号已注册'''

    def get(self, request, mobile):
        '''查询当前手机号的个数 要么0要么1'''
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'count': count, 'code': RETCODE.OK, 'errmsg': 'OK'})


class LoginView(View):
    '''用户账号登录'''

    def get(self, request):
        """提供登录界面"""
        return render(request, 'login.html')

    def post(self, request):
        """账号密码登录实现逻辑"""

        # 接收用户名
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        if all([username, password]) is False:
            return http.HttpResponseForbidden('缺少必传参数')
        # 校验
        # user = User.objects.get(username=username)
        # user.check_password(password)
        # 登录认证
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        #设置状态保持的周期
        if remembered != 'on':  # 没有勾选记住登录
            request.session.set_expiry(0)

        # 状态保持
        login(request, user)

        response = redirect(request.GET.get('next') or '/' )#创建响应对象
        response.set_cookie('username',user.username,max_age=60*60)
        # 响应结果重定向到首页
        return response


class LogoutView(View):
    """退出登录"""

    def get(self,request):
        #清除session中的状态保持数据
        logout(request)

        #清除cookie中的username
        response = redirect(reverse('users:login')) #redirect('/login/')
        response.delete_cookie('username')

        #重定向到login界面
        return response


class UserInfoView(mixins.LoginRequiredMixin,View):
    '''用户个人信息'''

    def get(self,requeset):
        """提供用户中心界面"""
        # 如果用户登录,返回用户中心界面
        # 如果没有登录 返回登录界面
        # user = requeset.user
        # if user.is_authenticated:
        #     return render(requeset,'user_center_info.html')
        # else:
        #     return redirect('/login/?next=/info/')

        return render(requeset, 'user_center_info.html')
