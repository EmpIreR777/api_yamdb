from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.response import Response

from .mixins import CreateListDeleteViewSet
from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleSerializer)
from reviews.models import Category, Genre, Review, Title


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
