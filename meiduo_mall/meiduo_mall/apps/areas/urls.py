from django.conf.urls import url

from . import views


urlpatterns = [
    # 省市区数据查询
    url(r'^areas/$', views.AreasView.as_view()),
]