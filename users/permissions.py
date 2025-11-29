from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Проверяет, является ли пользователь авторизованным и модератором"""

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return request.user.is_authenticated and request.user.groups.filter(name="moderators").exists()


class NotModerator(BasePermission):
    """Проверяет, что пользователь не модератор"""

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return not request.user.groups.filter(name="moderators").exists()


class IsOwner(BasePermission):
    """Проверяет, является ли пользователь авторизованным и владельцем"""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.owner == request.user


class IsProfileOwner(BasePermission):
    """Разрешает редактирование только владельцу профиля"""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.id == request.user.id
