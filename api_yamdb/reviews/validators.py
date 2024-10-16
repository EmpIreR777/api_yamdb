import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year_not_future(value):
    if value > timezone.now().year:
        raise ValidationError(
            'Год выпуска не может быть больше текущего'
        )


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
