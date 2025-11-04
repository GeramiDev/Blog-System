from rest_framework import permissions

"""

When a user wants to post a comment,
they must be a member,
but if they just want to read the comments,
membership is not required.

"""


class IsAuthenticatedOrGuest(permissions.BasePermission):
    def has_permission(self, request, view):
        # The GET method is open to everyone
        if request.method == "GET":
            return True

        # If user Logged
        if request.user and request.user.is_authenticated:
            return True

        return False
