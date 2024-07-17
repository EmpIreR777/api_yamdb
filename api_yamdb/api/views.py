from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from rest_framework import filters, mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer,
    ReviewSerializer)

from reviews.models import Title


class GetPostViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(GetPostViewSet):
    serializer_class = CategorySerializer


class GenreViewSet(GetPostViewSet):
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'category__slug',
        'genre__slug',
        'name',
        'year',
    )


class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer

    def get_title(self):
        return get_object_or_404(
            Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)
