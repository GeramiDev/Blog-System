from rest_framework import permissions

"""

In this class, we designed a custom access so
that everyone can view user profiles,
but only the owner of the account can edit the information.

"""


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # If the user requests to read in safe mode, there is no need to check anything
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user.id == request.user.id  # Change only for the profile owner
