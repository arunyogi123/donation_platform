from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_staff:
            return True
        owner_field = (
            getattr(obj, "user", None)
            or getattr(obj, "donor", None)
            or getattr(getattr(obj, "campaign", None), "user", None)
        )
        return owner_field == request.user