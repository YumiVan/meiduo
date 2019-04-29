from django.conf.urls import url,include
from . import views

urlpatterns = [
    url(r'^qq/authorization/$', views.OAuthURLView.as_view()),
    # QQ登录成功后的回调处理
    url(r'^oauth_callback/$', views.OAuthUserView.as_view()),

]
