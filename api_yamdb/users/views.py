from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer
import random

User = get_user_model()


class UserRegistrationView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            confirmation_code = random.randint(1000, 9999)
            user.confirmation_code = confirmation_code
            user.is_active = False
            user.save()
            send_mail(
                'Подтверждение регистрации',
                f'Ваш код подтверждения: {confirmation_code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response(
                {'message': 'Код отправлен на вашу электронную почту.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmRegistrationView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        try:
            user = User.objects.get(
                username=username, confirmation_code=confirmation_code)
            user.is_active = True
            user.confirmation_code = ''
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'Неправильное имя пользователя или код '},
                status=status.HTTP_400_BAD_REQUEST
            )
