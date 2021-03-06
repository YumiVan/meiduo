from django.shortcuts import render
from django_redis import get_redis_connection
from decimal import Decimal
import json
from django.views import View
from django import http
from django.utils import timezone
from django.db import transaction
from meiduo_mall.utils.views import LoginRequiredView
from users.models import Address
from goods.models import SKU
from .models import OrderInfo, OrderGoods
from meiduo_mall.utils.response_code import RETCODE


class OrderSettlementView(LoginRequiredView):
    """去结算界面"""

    def get(self, request):
        user = request.user
        # 获取当前登录用户的所有收货地址
        addresses = Address.objects.filter(user=user, is_deleted=False)
        # 如果有收货地址什么也不做,没有收货地址把变量设置为None
        addresses = addresses if addresses.exists() else None

        # 创建redis连接对象
        redis_conn = get_redis_connection('carts')
        # 获取hash所有数据{sku_id: count}
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        # 获取set集合数据{sku_id}
        cart_selected = redis_conn.smembers('selected_%s' % user.id)

        cart_dict = {}  # 准备一个字典,用来装勾选商品id及count  {1: 2}
        for sku_id_bytes in cart_selected:  # 遍历set集合
            # 将勾选的商品sku_id 和count装入字典,并都转换为int类型
            cart_dict[int(sku_id_bytes)] = int(redis_cart[sku_id_bytes])

        # 通过set集合中的sku_id查询到对应的所有sku模型
        sku_qs = SKU.objects.filter(id__in=cart_dict.keys())  # 此处bytes类型会自动转换

        total_count = 0  # 记录总数量
        total_amount = Decimal('0.00')  # 商品总价
        # 遍历sku_qs查询集给每个sku模型多定义count和amount属性
        for sku in sku_qs:
            count = cart_dict[sku.id]  # 获取当前商品的购买数量
            sku.count = count  # 把当前商品购物车数据绑定到sku模型对象上
            sku.amount = sku.price * count

            total_count += count  # 累加购买商品总数量
            total_amount += sku.amount  # 累加商品总价

        freight = Decimal('10.00')  # 运费

        context = {
            'addresses': addresses,  # 用户收货地址
            'skus': sku_qs,  # 勾选的购物车商品数据
            'total_count': total_count,  # 勾选商品总数量
            'total_amount': total_amount,  # 勾选商品总价
            'freight': freight,  # 运费
            'payment_amount': total_amount + freight  # 实付款
        }
        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequiredView):
    """提交订单"""

    def post(self, request):

        # 接收前端传入的收货地址,及支付方式
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 校验
        if all([address_id, pay_method]) is False:
            return http.HttpResponseForbidden('缺少必传参数')

        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('收货有误')

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM.get('CASH'), OrderInfo.PAY_METHODS_ENUM.get('ALIPAY')]:#[1,2]
            return http.HttpResponseForbidden('支付方式有误')

        # 20190511121110 + %09d % user.id
        user = request.user
        # 生成订单编号
        # order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

        # 订单状态
        status = (OrderInfo.ORDER_STATUS_ENUM.get('UNPAID')
                  if pay_method == OrderInfo.PAY_METHODS_ENUM.get('ALIPAY')
                  else OrderInfo.ORDER_STATUS_ENUM.get('UNSEND'))


        with transaction.atomic():#手动创建事务


            # 创建事务保存点
            save_point = transaction.savepoint()
            try:
                # 创建一个订单基本信息模型 并存储
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0.00'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=status
                )

                # 创建redis连接
                redis_conn = get_redis_connection('carts')
                # 获取hash数据
                redis_cart = redis_conn.hgetall('carts_%s' % user.id)
                # 获取set集合数据
                cart_selected = redis_conn.smembers('selected_%s' % user.id)
                cart_dict = {}
                # 遍历set把要购买的sku_id和count包装到一个新字典中{1:2}
                for sku_id_bytes in cart_selected:
                    cart_dict[int(sku_id_bytes)] = int(redis_cart[sku_id_bytes])

                # 遍历用来包装所有要购买商品的字典
                for sku_id in cart_dict:
                    while True:
                        # 通过sku_id获取到sku模型
                        sku = SKU.objects.get(id=sku_id)
                        # 获取当前商品要购买的数量
                        buy_count = cart_dict[sku_id]
                        # 获取当前商品的库存和销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # 判断库存
                        if buy_count > origin_stock:
                            # 回滚
                            transaction.savepoint_rollback(save_point)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        new_stock = origin_stock - buy_count  # 计算新的库存
                        new_sales = origin_sales + buy_count  # 计算新的销量
                        # # 修改sku的 库存
                        # sku.stock = new_stock
                        # # 修改sku的销量
                        # sku.sales = new_sales
                        # sku.save()

                        #乐观锁解决抢夺时候数据库写入脏数据
                        result = SKU.objects.filter(id=sku_id,stock=origin_stock).update(stock=new_stock,sales=new_sales)
                        if result == 0:#如果下单失败,给他无限次下单机会,直到成功,或库存不足
                            continue

                        # 修改spu的销量
                        sku.spu.sales += buy_count
                        sku.spu.save()

                        # 存储订单商品记录
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=buy_count,
                            price=sku.price
                        )

                        order.total_count += buy_count  # 累加订单商品总数量
                        order.total_amount += (sku.price * buy_count)  # 累加商品总价
                        break

                order.total_amount += order.freight  # 累加运费
                order.save()
            except Exception:
                transaction.savepoint_rollback(save_point)  # 回滚
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})
            else:
                transaction.savepoint_commit(save_point)  # 提交事务


        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *cart_selected)  # 删除hash中已经购买商品数据{2: 1}
        pl.delete('selected_%s' % user.id)
        pl.execute()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '提交订单成功', 'order_id': order_id})


class OrderSuccessView(LoginRequiredView):
    """展示提交订单成功界面"""

    def get(self, request):

        # 接收查询参数
        query_dict = request.GET
        order_id = query_dict.get('order_id')
        payment_amount = query_dict.get('payment_amount')
        pay_method = query_dict.get('pay_method')

        # 校验
        try:
            OrderInfo.objects.get(order_id=order_id, pay_method=pay_method, total_amount=payment_amount)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单有误')



        # 包装要传给模板的数据
        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }

        return render(request, 'order_success.html', context)


class OrderCommentView(LoginRequiredView):

    def get(self,request):
        """展示订单评价界面"""
        # 接受查询参数
        order_id = request.GET.get('order_id')
        # 校验
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=request.user,
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单有误')
        # 查询当前订单中所有未评价的商品
        # order_goods_qs = order.skus.filter(is_commented=False)
        order_goods_qs = OrderGoods.objects.filter(order=order,is_commented=False)
        # 构造前端渲染需要的数据
        uncomment_goods_list = []
        for order_goods in order_goods_qs:
            sku = order_goods.sku
            uncomment_goods_list.append({
                'order_id': order_id,
                'sku_id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': str(sku.price),
                'score': order_goods.score,
                'comment': order_goods.comment,
                'is_anonymous': str(order_goods.is_anonymous),
                'is_comment': str(order_goods.is_commented)
            })

        context = {
            'uncomment_goods_list': uncomment_goods_list
        }
        return render(request, 'goods_judge.html', context)


    def post(self,request):
        """提交评价信息"""
        #获取请求体中的数据
        json_dict = json.loads(request.body.decode())
        order_id = json_dict.get('order_id')
        sku_id = json_dict.get('sku_id')
        comment = json_dict.get('comment')
        score = json_dict.get('score')
        is_anonymous = json_dict.get('is_anonymous')

        # 校验
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=request.user, status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息有误')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku不存在')

        if isinstance(is_anonymous, bool) is False: #是不是布尔类型
            return http.HttpResponseForbidden('参数类型有误')

        # 修改OrderGoods中的评价信息
        OrderGoods.objects.filter(sku_id=sku_id,order_id=order_id,is_commented=False).update(
            is_anonymous=is_anonymous,
            score=score,
            comment=comment,
            is_commented=True
        )
        # 修改sku和spu的评价量
        sku.comments += 1
        sku.save()

        sku.spu.comments += 1
        sku.spu.save()
        # 判断订单中的商品是否全部评价完成,如果都评价后将订单状态修改为已完成
        if OrderGoods.objects.filter(order_id=order_id, is_commented=False).count() == 0:
            order.status = OrderInfo.ORDER_STATUS_ENUM['FINISHED']
            order.save()

        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class GoodsCommentView(View):
    """获取评价信息"""

    def get(self, request, sku_id):
        # 校验
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku不存在')

        # 获取OrderGoods中的当前sku_id的所有OrderGoods
        order_goods_qs = OrderGoods.objects.filter(sku_id=sku_id, is_commented=True).order_by('-create_time')

        comments = []
        # 构造前端需要的数据格式  username, score , comment
        for order_goods in order_goods_qs:
            username = order_goods.order.user.username  # 获取当前订单商品所属用户名

            comments.append({
                'username': (username[0] + '***' + username[-1]) if order_goods.is_anonymous else username,
                'score': order_goods.score,
                'comment': order_goods.comment
            })

        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'comment_list': comments})



