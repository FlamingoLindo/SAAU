from rest_framework.permissions import BasePermission

class IsStaffUser(BasePermission):

    def has_staff_permission(self, request, view):
        return bool(request.user and request.user.is_staff)
