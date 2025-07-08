from rest_framework import permissions


class IsMessageOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a message.
    """

    def has_object_permission(self, request, view, obj):
        return obj.recipient == request.user.profile
