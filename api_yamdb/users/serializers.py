import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'bio': {'default': ''},
        }

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать "me" в качестве имени пользователя запрещено.'
            )
        if len(value) > 150:
            raise serializers.ValidationError(
                'Имя пользователя должно содержать не более 150 символов.'
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Имя пользователя должно соответствовать шаблону'
            )
        return value

    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError(
                'Электронная почта должна содержать не более 254 символов.'
            )
        return value

    def validate_first_name(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                'Имя должно содержать не более 150 символов.'
            )
        return value

    def validate_last_name(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                'Фамилия должна содержать не более 150 символов.'
            )
        return value


class UserRegistrationSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['email', 'username']


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        pass


class UserCreateSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['password']
        extra_kwargs = {
            **BaseUserSerializer.Meta.extra_kwargs,
            'password': {'required': False, 'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['username', 'email', 'first_name', 'last_name', 'bio']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }
