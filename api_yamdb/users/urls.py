from django.urls import path

from .views import UserRegistrationView, ConfirmRegistrationView

urlpatterns = [
    path(
        'signup/', UserRegistrationView.as_view(), name='signup'
    ),
    path(
        'token/', ConfirmRegistrationView.as_view(), name='token_obtain_pair'
    ),
]
