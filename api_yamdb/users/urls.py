from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

v1_router = DefaultRouter()
v1_router.register('', views.UserViewSet, basename='user')

urlpatterns = [
    path(
        'signup/', views.UserRegistrationView.as_view(),
        name='signup'
    ),
    path(
        'token/', views.ConfirmRegistrationView.as_view(),
        name='confirm_registration'
    ),
    path('me/', views.UserSelfView.as_view(),
         name='user-self'),
    path('', include(v1_router.urls)),
]
