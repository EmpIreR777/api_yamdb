import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise ValidationError(
            'Требуется только буквы, цифры и @/./+/-/_.'
        )
    if value == 'me':
        raise ValidationError(
            'Использовать "me" в качестве имени пользователя запрещено.'
        )
    return value
