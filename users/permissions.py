from rest_framework import permissions


class IsModer(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором."""

    message = "Не в группе moders"

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moders").exists()


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем."""

    message = "Не владелец"

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False
