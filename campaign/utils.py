# from rest_framework.permissions import BasePermission
# from campaign.models import UserRole, RoleType


# class IsAdmin(BasePermission):

#     def has_permission(self, request, view):
#         qs = UserRole.objects.filter(user=request.user).first()

#         if qs:
#             if qs.role.name == RoleType.ADMIN:
#                 return True
#             return False
#         else:
#             return False


