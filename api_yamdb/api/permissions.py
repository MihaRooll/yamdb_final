from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Модератор"""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_admin))


class IsAdmin(permissions.BasePermission):
    """Админ"""
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_admin)


class IsAuthorOrAdministratorOrReadOnly(permissions.BasePermission):
    """Автор"""
    def has_permission(self, request, view):
        """Ограничения на уровне запроса"""
        return (
            request.method in permissions.SAFE_METHODS
            and request.user.is_anonymous
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Ограничения на уровне объекта"""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )
