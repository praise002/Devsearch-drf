from rest_framework import permissions

from apps.projects.models import Project


class IsProjectOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.method != "POST":
            return True

        slug = view.kwargs.get("slug")
        try:
            project = Project.objects.get(slug=slug)
            return project.owner == request.user.profile
        except Project.DoesNotExist:
            return False
