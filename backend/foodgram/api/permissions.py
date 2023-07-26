from rest_framework import permissions


class IsAuthOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view,) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_authenticated:
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


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(
            self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.username == obj.author:
            return True
        
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        return False
        
