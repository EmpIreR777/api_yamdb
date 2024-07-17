from rest_framework import routers
from django.urls import include, path

from .views import CategoryViewSet, GenreViewSet, TitleViewSet
from users import views

v1_router = routers.DefaultRouter()
v1_router.register('categorys', CategoryViewSet, basename='categorys')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('users', views.UserViewSet, basename='user')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path(
        'v1/auth/signup/', views.UserRegistrationView.as_view(),
        name='signup'
    ),
    path(
        'v1/auth/token/', views.ConfirmRegistrationView.as_view(),
        name='confirm_registration'
    ),
    path(
        'v1/users/me/', views.UserSelfView.as_view(),
        name='user-self'),
]
