import re

from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException


class CustomValidationError(APIException):

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A custom validation error occurred.'

    def __init__(self, detail=None, status_code=None):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code


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
