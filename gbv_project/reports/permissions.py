from rest_framework.permissions import BasePermission

class IsAdminOrLawEnforcement(BasePermission):
    """
    Allows access only to admin or law enforcement users.
    Assumes your User model has a `role` field.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "lawyer"]