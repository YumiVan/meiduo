from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.libs.captcha.captcha import captcha
from random import randint
from meiduo_mall.libs.yuntongxun.sms import CCP
from . import constants
import logging
logger = logging.getLogger('django')

# Create your views here.
class ImageCodeView(View):
    '''生产图形验证码'''
    def get(self,request,uuid):
        # 利用SDK生成图形验证码
        name ,text,image = captcha.generate_captcha()
        # 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # 将图形码存入redis
        redis_conn.setex('img_%s' %uuid,constants.IMAGE_CODE_REDIS_EXPRIE,text)
        # 把生成好的图片响应给前端
        return http.HttpResponse(image,content_type='image/png')

class SMSCodeView(View):

    '''短信验证码'''
    def get(self,request,mobile):
        # 每次来发短信之前先拿当前要发短信的手机号获取redis的短信标记，如果没有标记就发，有标记提前响应
        # 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '频繁发送短信'})

        #接收到前端传入的mobile,image_code,uuid
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        if all ([image_code_client,uuid] ) is False:
            return http.JsonResponse({'code':RETCODE.NECESSARYPARAMERR,'errmsg':'缺少必传参数'})


        # 根据uuid作为key获取到redis中当前用户的图形验证值
        image_code_server = redis_conn.get('img_%s' %uuid)
        # 删除图形验证码,让他只用一次 防止刷刷刷
        redis_conn.delete('img_%s'% uuid)
        # 从redis冲取出来的数据都是bytes类型


        # 判断用户写的图形验证码和我们redis存的是否一致
        if image_code_server is None or image_code_client.lower() != image_code_server.decode().lower():
            return http.JsonResponse({'code':RETCODE.IMAGECODEERR,'errmsg':'图形验证码错误'})

        # 发送短信
        # 利用随机模块生成一个6位数字
        sms_code = '%06d'% randint(0,99999)
        # print(sms_code)
        logger.info(sms_code)
        # 创建redis管道对象
        pl = redis_conn.pipeline()
        # 将生成好的短信验证码也存储到redis,以备后期校验
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPRIE, sms_code)
        # 手机号发过短信后在redis中存储一个标记

        pl.setex('send_flag_%s' % mobile, 60, 1)
        # 执行管道
        pl.execute()


        # 使用容联云SDK发短信

        CCP().send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPRIE // 60],constants.SEND_SMS_TEMPLATE_ID)
        #响应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'发送短信成功'})


