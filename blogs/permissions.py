from rest_framework import permissions

"""

In this class, we designed a custom permission for
ourselves so that no one can modify another user's post or
comment and can only read it.


"""


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # If the user requests to read in safe mode, there is no need to check anything.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
