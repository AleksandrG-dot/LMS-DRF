from rest_framework import permissions


class IsModer(permissions.BasePermission):
    message = "Не в группе moders"

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moders").exists()
