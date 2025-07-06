from rest_framework import permissions

from apps.projects.models import Project


class IsProjectOwner(permissions.BasePermission):
    # def has_permission(self, request, view):
    #     """
    #     Return `True` if permission is granted, `False` otherwise.
    #     """
    #     if request.method == "GET":
    #         return True

    #     slug = view.kwargs.get("slug")
    #     try:
    #         project = Project.objects.get(slug=slug)
    #         return project.owner == request.user.profile
    #     except Project.DoesNotExist:
    #         return False
    
    """
    Custom permission to only allow owners of a project to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the project.
        return obj.owner == request.user.profile  # or obj.owner == request.user.profile
