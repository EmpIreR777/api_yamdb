import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny

from .serializers import UserRegistrationSerializer, UserSerializer, UserCreateSerializer

User = get_user_model()


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')

        # Проверка наличия обязательных полей:
        missing_fields = []
        if not email:
            missing_fields.append('email')
        if not username:
            missing_fields.append('username')

        if missing_fields:
            return Response(
                {field: ['Это поле обязательно для заполнения.']
                    for field in missing_fields},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, существует ли пользователь с указанным email или username:
        user = User.objects.filter(email=email).first()
        if user:
            if User.objects.filter(username=username).first():
                # Если пользователь существует, обновляем его данные:
                user.username = username
                user.confirmation_code = random.randint(1000, 9999)
                user.is_active = False
                user.save()
            else:
                return Response(
                    {'error': 'Такой email или username уже существует.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            # Если пользователя не существует, создаем нового:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                user.confirmation_code = random.randint(1000, 9999)
                user.is_active = False
                user.save()
            else:
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

        send_mail(
            'Подтверждение регистрации',
            f'Ваш код подтверждения: {user.confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return Response(
            {'email': user.email, 'username': user.username},
            status=status.HTTP_200_OK
        )


class ConfirmRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        try:
            user = User.objects.get(username=username)
            if user.confirmation_code != confirmation_code:
                return Response(
                    {'error': 'Неправильный код подтверждения'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.is_active = True
            user.confirmation_code = ''
            user.save()

            # Создаем токен доступа
            access_token = AccessToken.for_user(user)

            return Response(
                {'token': str(access_token)},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # permission_classes = [permissions.IsAdminUser]
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save()


class UserSelfView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # def get(self, request):
    #     serializer = UserSerializer(request.user)
    #     return Response(serializer.data)

    # def patch(self, request):
    #     serializer = UserSerializer(
    #         request.user, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
