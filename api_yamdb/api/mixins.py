from rest_framework import filters, mixins
from rest_framework.viewsets import GenericViewSet


class CreateListDeleteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    lookup_url_kwarg = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CreateRetrieveListDeleteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
