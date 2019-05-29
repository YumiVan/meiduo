from rest_framework import serializers

from users.models import User


class AdminAuthSerializer(serializers.ModelSerializer):
    """管理员登录序列化器类"""
    token = serializers.CharField(label='JWT token', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'token')

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    # 补充验证
    def validate(self, attrs):
        """用户名和密码正确"""
        pass


    def create(self, validated_data):
        # 生成jwt token，保存登录用户身份信息
        pass