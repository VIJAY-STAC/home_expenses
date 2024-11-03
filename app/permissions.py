from rest_framework import permissions


class IsInternalAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_internal_admin