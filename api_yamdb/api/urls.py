from rest_framework import routers
from django.urls import include, path

from .views import CategoryViewSet, GenreViewSet, TitleViewSet

v1_router = routers.DefaultRouter()
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genre')
v1_router.register('titles', TitleViewSet, basename='title')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/', include('users.urls')),
]
