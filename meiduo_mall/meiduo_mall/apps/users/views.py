from django.shortcuts import render, redirect
from django.views import View
from django import http
import re
from django.contrib.auth import login, logout
from django.db import DatabaseError
from meiduo_mall.utils.response_code import RETCODE

from .models import User
import logging

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
        # TODO 短信验证码校验后期补充

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
        return redirect('/')


class UsernameCountView(View):
    '''判断用户名已注册'''

    def get(self, request, username):
        '''查询当前用户名的个数 要么0要么1'''
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'count': count, 'code': RETCODE.OK, 'errmsg': 'OK'})


class MobileCountView(View):
    '''判断用户名已注册'''

    def get(self, request, mobile):
        '''查询当前用户名的个数 要么0要么1'''
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'count': count, 'code': RETCODE.OK, 'errmsg': 'OK'})
