from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from users.models import User


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器类"""
    class Meta:
        model = Permission
        fields = '__all__'


class ContentTypeSerializer(serializers.ModelSerializer):
    """权限类型序列化器类"""
    class Meta:
        model = ContentType
        fields = ('id', 'name')


class GroupSerializer(serializers.ModelSerializer):
    """用户组序列化器类"""
    class Meta:
        model = Group
        fields = '__all__'


class PermissionSimpleSerializer(serializers.ModelSerializer):
    """权限序列化器类"""
    class Meta:
        model = Permission
        fields = ('id', 'name')


class AdminSerializer(serializers.ModelSerializer):
    """管理员序列化器类"""
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'groups', 'user_permissions', 'password')

        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False,
                'allow_blank': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '密码最小长度为8',
                    'max_length': '密码最大长度为20'
                }
            },
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '用户名最小长度为8',
                    'max_length': '用户名最大长度为20'
                }
            }
        }

    def create(self, validated_data):
        # 处理密码
        password = validated_data.get('password')

        if not password:
            # 设置默认密码
            password = '123456abc'
            validated_data['password'] = password

        validated_data['is_staff'] = True

        # 新增管理员
        user = super().create(validated_data)

        # 设置密码进行加密
        user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        # 处理密码
        password = validated_data.get('password')

        # 更新管理员
        user = super().update(instance, validated_data)

        if password:
            # 重新设置用户的密码
            user.set_password(password)
            user.save()

        return user






class GroupSimpleSerializer(serializers.ModelSerializer):
    """用户组序列化器类"""
    class Meta:
        model = Group
        fields = ('id', 'name')









