from django.conf.urls import url
from meiduo_admin.views import users, statistical, channels, skus, spus, orders, permissions

urlpatterns = [
    url(r'^authorizations/$', users.AdminAuthView.as_view()),

    # 数据统计
    url(r'^statistical/total_count/$', statistical.UserTotalCountView.as_view()),
    url(r'^statistical/day_increment/$', statistical.UserDayIncrementView.as_view()),
    url(r'^statistical/day_active/$', statistical.UserDayActiveView.as_view()),
    url(r'^statistical/day_orders/$', statistical.UserDayOrderView.as_view()),
    url(r'^statistical/month_increment/$', statistical.UserMonthIncrementView.as_view()),
    url(r'^statistical/goods_day_views/$', statistical.GoodsDayViewsView.as_view()),

    # 用户管理
    url(r'^users/$', users.UserInfoView.as_view()),

    # 频道管理
    url(r'^goods/channel_types/$', channels.ChannelTypesView.as_view()),
    url(r'^goods/categories/$', channels.ChannelCategoryView.as_view()),

    # SKU图片管理
    url(r'^skus/simple/$', skus.SKUSimpleView.as_view()),

    # SKU商品管理
    url(r'^goods/simple/$', spus.SPUSimpleView.as_view()),
    url(r'^skus/categories/$', skus.SKUCategoriesView.as_view()),
    url(r'^goods/(?P<pk>\d+)/specs/$', spus.SPUSpecView.as_view()),

    # 权限管理
    url(r'^permission/content_types/$', permissions.PermissionViewSet.as_view({
        'get': 'content_types'
    })),

    # 用户组管理
    url(r'^permission/simple/$', permissions.GroupViewSet.as_view({
        'get': 'simple'
    })),

    # 管理员管理
    url(r'^permission/groups/simple/$', permissions.AdminViewSet.as_view({
        'get': 'simple'
    }))
]

# 频道管理
from rest_framework.routers import DefaultRouter
# 1. 创建路由对象
router = DefaultRouter()
# 2. 注册视图集
router.register('goods/channels', channels.ChannelViewSet, base_name='channels')
# 3. 将生成url配置项列表添加到urlpatterns中
urlpatterns += router.urls

# SKU图片管理
router = DefaultRouter()
router.register('skus/images', skus.SKUImageViewSet, base_name='images')
urlpatterns += router.urls

# SKU商品管理
router = DefaultRouter()
router.register('skus', skus.SKUViewSet, base_name='skus')
urlpatterns += router.urls

# 订单管理
router = DefaultRouter()
router.register('orders', orders.OrdersViewSet, base_name='orders')
urlpatterns += router.urls


# 权限管理
router = DefaultRouter()
router.register('permission/perms', permissions.PermissionViewSet, base_name='perms')
urlpatterns += router.urls


# 用户组管理
router = DefaultRouter()
router.register('permission/groups', permissions.GroupViewSet, base_name='groups')
urlpatterns += router.urls

# 管理员管理
router = DefaultRouter()
router.register('permission/admins', permissions.AdminViewSet, base_name='admins')
urlpatterns += router.urls
