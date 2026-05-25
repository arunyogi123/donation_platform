from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        owner_field = getattr(obj, "user", None) or getattr(obj, "donor", None)
        return request.user.is_staff or owner_field == request.user