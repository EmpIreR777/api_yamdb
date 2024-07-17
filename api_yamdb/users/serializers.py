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
