from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserRegistrationView, ConfirmRegistrationView

router = DefaultRouter()
# router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path(
        'signup/', UserRegistrationView.as_view(), name='signup'
    ),
    path(
        'token/', ConfirmRegistrationView.as_view(), name='confirm_registration'
    ),
    path('', include(router.urls)),
    # path('users/me/', UserSelfView.as_view(), name='user-self'),
]
