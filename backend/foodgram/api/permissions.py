from rest_framework import permissions


class IsAuthOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view,) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_admin:
            return True
        return False


class IsAdminUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser is True or request.user.id == obj.user.id:
            return True
        return False


class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return False
        return True
