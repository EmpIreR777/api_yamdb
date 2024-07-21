import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role']

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Требуется только буквы, цифры и @/./+/-/_.'
            )
        return value


class UserRegistrationSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        pass


class UserSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        pass


class UserUpdateSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        fields = ['username', 'email', 'first_name', 'last_name', 'bio']
