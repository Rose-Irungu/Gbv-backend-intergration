from rest_framework.permissions import BasePermission

class IsAdminOrLawEnforcement(BasePermission):
    """
    Allows access only to admin or law enforcement users.
    Assumes your User model has a `role` field.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "lawyer"]
    
class IsOwnerOrProfessional(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if hasattr(obj, 'report'):
            return (obj.report.reporter == request.user or 
                    obj.professional == request.user)
        return obj.created_by == request.user

class CanAccessCase(BasePermission):
    def has_permission(self, request, view):
        if request.user.role in ['admin', 'doctor', 'lawyer', 'counselor']:
            return True
        return request.user.role == 'survivor'