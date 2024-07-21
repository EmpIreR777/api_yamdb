from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthor(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj == request.user
