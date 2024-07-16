from rest_framework import routers
from django.urls import include, path

from .views import CategoryViewSet, GenreViewSet, TitleViewSet

v1_router = routers.DefaultRouter()
v1_router.register('category', CategoryViewSet, basename='category')
v1_router.register('genre', GenreViewSet, basename='genre')
v1_router.register('title', TitleViewSet, basename='title')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
