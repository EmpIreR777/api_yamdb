from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.response import Response

from .mixins import CreateListDeleteViewSet, CreateRetrieveListDeleteViewSet
from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer,
)
from reviews.models import Category, Genre, Title

class CategoryViewSet(CreateListDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Category, slug=self.kwargs['slug'])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(CreateListDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Genre, slug=self.kwargs['slug'])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TitleViewSet(CreateRetrieveListDeleteViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year',)
