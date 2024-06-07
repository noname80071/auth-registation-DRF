from django.contrib.auth.hashers import make_password
from rest_framework import serializers, status

from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def validate(self, attrs):
        data = super(UserSerializer, self).validate(attrs)
        if data['password'] == data['confirm_password'] and 6 <= len(data['password']) <= 12:
            if not User.objects.filter(email=data['email']).exists():
                del data['confirm_password']
                return data
            raise serializers.ValidationError('Неверная почта', code=status.HTTP_400_BAD_REQUEST)
        raise serializers.ValidationError('Неверный пароль!', code=status.HTTP_400_BAD_REQUEST)


class VerificationCodeSerializer(serializers.Serializer):
    code = serializers.CharField()
