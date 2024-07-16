from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.viewsets import GenericViewSet
from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer,
)


class GetPostViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
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
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year',)
