import re

from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать "me" в качестве имени пользователя запрещено.'
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Username должен содержать буквы, цифры и символы @/./+/-/_'
            )
        if len(value) > 150:
            raise serializers.ValidationError(
                'Username должен быть не более 150 символов.'
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'bio': {'default': ''},
        }


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role', 'password']
        extra_kwargs = {            
            'username': {'required': True},
            'email': {'required': True},
            'password': {'required': False, 'write_only': True},
            'bio': {'default': ''},
        }

    def validate_username(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                "Username must be 150 characters or fewer."
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                "Username must match the pattern: ^[\w.@+-]+\Z"
            )
        return value

    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError(
                "Email must be 254 characters or fewer."
            )
        return value

    def validate_first_name(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                "First name must be 150 characters or fewer."
            )
        return value

    def validate_last_name(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                "Last name must be 150 characters or fewer."
            )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
