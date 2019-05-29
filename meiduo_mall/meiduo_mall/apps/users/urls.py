from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required
urlpatterns = [
    url(r'register/$',views.RegisterView.as_view(),name='register'),
    #判断用户名是否已注册
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$',views.UsernameCountView.as_view()),
    #判断手机号是否已注册
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',views.MobileCountView.as_view()),
    # 用户登录
    url(r'^login/$',views.LoginView.as_view(),name='login'),
    # 退出登录
    url(r'^logout/$',views.LogoutView.as_view(),),
    # 用户中心
    url(r'^info/$',login_required(views.UserInfoView.as_view()),name='info'),
    # 设置用户邮箱
    url(r'^emails/$', views.EmailView.as_view()),
    # 激活邮箱
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
    # 用户收货地址查询
    url(r'^addresses/$', views.AddressView.as_view(),name='address'),
    # 用户新增收货地址
    url(r'^addresses/create/$', views.CreateAddressView.as_view()),
    # 用户收货地址修改和删除
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    # 用户设置默认地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
    # 修改用户地址标题
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),
    # 修改用户密码
    url(r'^password/$', views.ChangePasswordView.as_view()),
    # 浏览记录
    url(r'^browse_histories/$', views.UserBrowseHistory.as_view()),
    # 用户全部订单
    url(r'^orders/info/(?P<page_num>\d+)/$', views.UserOrderInfoView.as_view()),
    #密码找回界面
    url(r'^find_password/$', views.FindPassword.as_view(),name='find_password'),
    #密码找回第一步
    url(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/sms/token/$', views.FindPassword1.as_view()),
    #密码找回第二步
    url(r'^sms_codes/$', views.FindPassword2.as_view()),
    #找回密码第二步2-1
    url(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/password/token/$', views.FindPassword2_1.as_view()),
    #找回密码第三步
    url(r'^users/(?P<user_id>\d+)/password/$', views.FindPassword3.as_view()),
]



