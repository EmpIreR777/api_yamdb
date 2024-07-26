from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.forms import ValidationError
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
    IsAdminOrReadOnly, IsAuthorOrReadOnly, IsAdmin
)
from .serializers import (
    CategorySerializer, CommentSerializer, ConfirmRegistrationSerializer,
    GenreSerializer, ReviewSerializer, TitleSerializer,
    TitleCreateUpdateSerializer, UserRegistrationSerializer, UserSerializer,
    UserUpdateSerializer
)
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class CategoryViewSet(CreateListDeleteViewSet):
    """Получение категории, добавление и удаление."""

    queryset = Category.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDeleteViewSet):
    """Получение жанра, добавление и удаление."""

    queryset = Genre.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Получение произведения, частичное обновление, добавление и удаление."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleCreateUpdateSerializer
        return TitleSerializer

    def get_queryset(self):
        return Title.objects.all().select_related('category').prefetch_related(
            'genre').annotate(rating=Avg('reviews__score'))


class ReviewViewSet(viewsets.ModelViewSet):
    """Получение обзора, частичное обновление, добавление и удаление."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

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
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

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

    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        user = User.objects.filter(email=email).first()
        if user:
            confirmation_code = default_token_generator.make_token(user)
        else:
            user = User.objects.create_user(username=username, email=email)
            user.is_active = False
            user.save()
            confirmation_code = default_token_generator.make_token(user)

        send_mail(
            'Подтверждение регистрации',
            f'Ваш код подтверждения: {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        response_serializer = self.serializer_class(user)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ConfirmRegistrationView(APIView):
    """
    Представление для подтверждения регистрации пользователя.

    Доступно для всех пользователей (без аутентификации).
    Принимает POST-запрос с полями username и confirmation_code
    для подтверждения регистрации.
    При успешном подтверждении активирует учетную запись пользователя
    и возвращает токен доступа.
    """

    permission_classes = (AllowAny,)
    serializer_class = ConfirmRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            user.is_active = True
            user.save()

            access_token = AccessToken.for_user(user)

            return Response(
                {'token': str(access_token)},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления пользователями.

    Доступно только для аутентифицированных пользователей
    с правами администратора.
    Поддерживает операции создания, частичного обновления,
    удаления и поиска пользователей.
    """

    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAuthenticated, IsAdmin)
    queryset = User.objects.all()
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ['username', 'email', 'first_name', 'last_name']


class UserSelfView(APIView):
    """
    Представление для получения и частичного обновления данных
    текущего пользователя.

    Доступно только для аутентифицированных пользователей.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
