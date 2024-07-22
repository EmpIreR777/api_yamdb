from rest_framework import routers
from django.urls import include, path

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet,
    UserRegistrationView,
    ConfirmRegistrationView,
    UserSelfView,
    UserViewSet
)


v1_router = routers.DefaultRouter()
v1_router.register(r'categories', CategoryViewSet,
                   basename='categories')
v1_router.register(r'genres', GenreViewSet,
                   basename='genres')
v1_router.register(r'titles', TitleViewSet,
                   basename='titles')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)
v1_router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path(
        'v1/auth/signup/', UserRegistrationView.as_view(),
        name='signup'
    ),
    path(
        'v1/auth/token/', ConfirmRegistrationView.as_view(),
        name='confirm_registration'
    ),
    path('v1/users/me/', UserSelfView.as_view(),
         name='user-self'),
    path('v1/', include(v1_router.urls)),
]
