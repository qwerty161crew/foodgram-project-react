from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff or request.user.is_superuser:
            return True
        return False


class IsAdminUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser is True or request.user.id == obj.user.id:
            return True
        return False


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(
            self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user == obj.author:
            return True
        print('False')
        return False


class IsAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
        )
