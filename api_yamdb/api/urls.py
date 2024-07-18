from rest_framework import routers
from django.urls import include, path

from .views import (
    CategoryViewSet, GenreViewSet, TitleViewSet, ReviewViewSet,
    CommentViewSet)
from users import views



v1_router = routers.DefaultRouter()
v1_router.register(r'categories', CategoryViewSet, basename='categories')
v1_router.register(r'genres', GenreViewSet, basename='genres')
v1_router.register(r'titles', TitleViewSet, basename='titles')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [    
    path('v1/', include(v1_router.urls)),
]
