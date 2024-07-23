from django.core.exceptions import ValidationError


def validate_not_me(value):
    if value == 'me':
        raise ValidationError(
            'Использовать "me" в качестве имени пользователя запрещено.'
        )
