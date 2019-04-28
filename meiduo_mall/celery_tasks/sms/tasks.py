# 编写异步代码
# 启动命令 celery -A celery_tasks.main worker -l info
from celery_tasks.sms.yuntongxun.sms import CCP
from celery_tasks.main import celery_app

@celery_app.task(name = 'send_sms_code') #此装饰器作用是让下面的函数真正的成为celery的任务
def send_sms_code(mobile,sms_code):
    """
    利用celery异步发送短信
    :param mobile: 要收到短信的手机号
    :param sms_code: 短信验证码
    """
    CCP().send_template_sms(mobile, [sms_code, 5], 1)