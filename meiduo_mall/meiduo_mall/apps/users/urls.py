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
    # url(r'^info/$',login_required(views.UserInfoView.as_view()),name='info'),
    url(r'^info/$',login_required(views.UserInfoView.as_view()),name='info'),

]