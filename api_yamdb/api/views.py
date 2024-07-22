import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .mixins import CreateListDeleteViewSet
from .filters import TitleFilter
from .permissions import (
    IsAdminOrReadOnly, IsAuthorOrReadOnly,
    IsAdmin, IsAuthor
)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleSerializer, UserRegistrationSerializer,
    UserSerializer, UserUpdateSerializer
)
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class CategoryViewSet(CreateListDeleteViewSet):
    """Получение категории, добавление и удаление."""

    queryset = Category.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Category, slug=self.kwargs['slug'])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(CreateListDeleteViewSet):
    """Получение жанра, добавление и удаление."""

    queryset = Genre.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = GenreSerializer

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Genre, slug=self.kwargs['slug'])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TitleViewSet(viewsets.ModelViewSet):
    """Получение произведения, частичное обновление, добавление и удаление."""

    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def update(self, request, *args, **kwargs):
        if not kwargs.get('partial'):
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        category = get_object_or_404(
            Category,
            slug=self.request.data['category'],
        )
        genres = [
            get_object_or_404(
                Genre,
                slug=genre,
            ) for genre in self.request.data.getlist('genre')
        ]
        serializer.save(category=category, genre=genres,)

    def perform_update(self, serializer):
        if 'category' in self.request.data:
            serializer.validated_data['category'] = get_object_or_404(
                Category,
                slug=self.request.data['category'],
            )
        serializer.save()


class ReviewViewSet(viewsets.ModelViewSet):
    """Получение обзора, частичное обновление, добавление и удаление."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def update(self, request, *args, **kwargs):
        if not kwargs.get('partial'):
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    def get_title(self):
        return get_object_or_404(
            Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Получение комментариев, частичное обновление, добавление и удаление."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def update(self, request, *args, **kwargs):
        if not kwargs.get('partial'):
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    def get_review(self):
        return get_object_or_404(
            Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)


class UserRegistrationView(APIView):
    """
    Представление для регистрации пользователя.

    Доступно для всех пользователей (без аутентификации).
    Принимает POST-запрос с полями email и username
    для регистрации нового пользователя.
    Отправляет код подтверждения на указанный email.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        required_fields = ['email', 'username']
        missing_fields = [
            field for field in required_fields if not request.data.get(field)
        ]

        if missing_fields:
            return Response(
                {field: ['Это поле обязательно для заполнения.']
                    for field in missing_fields},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = request.data.get('email')
        username = request.data.get('username')

        user = User.objects.filter(email=email).first()
        if user:
            if User.objects.filter(username=username).first():
                user.username = username
                user.confirmation_code = random.randint(100000, 999999)
                user.is_active = False
                user.save()
            else:
                return Response(
                    {'error': 'Такой email или username уже существует.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            serializer = UserRegistrationSerializer(
                data=request.data
            )
            if serializer.is_valid():
                user = serializer.save()
                user.confirmation_code = random.randint(100000, 999999)
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
    """
    Представление для подтверждения регистрации пользователя.

    Доступно для всех пользователей (без аутентификации).
    Принимает POST-запрос с полями username и confirmation_code
    для подтверждения регистрации.
    При успешном подтверждении активирует учетную запись пользователя
    и возвращает токен доступа.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        # Проверяем наличие обязательных полей:
        if not username or not confirmation_code:
            return Response(
                {'error': 'Отсутствует обязательное поле или оно некорректно'},
                status=status.HTTP_400_BAD_REQUEST
            )

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
    """
    Вьюсет для управления пользователями.

    Доступно только для аутентифицированных пользователей
    с правами администратора.
    Поддерживает операции создания, частичного обновления,
    удаления и поиска пользователей.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all()
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSelfView(APIView):
    """
    Представление для получения и частичного обновления данных
    текущего пользователя.

    Доступно только для аутентифицированных пользователей.
    """

    permission_classes = [IsAuthenticated, IsAuthor]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
