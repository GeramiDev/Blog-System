from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializer import (
    RegisterSerializer,
    ProfileSerializer,
    ChangePasswordSerializer,
    RequestEmailChangeSerializer,
    VerifyEmailChangeSerializer,
    RequestPasswordResetSerializer,
    ConfirmPasswordResetSerializer,
)
from .models import Profile
from .permissions import IsOwnerOrReadOnly

# Creating access to the model in this module
User = get_user_model()


# This class inherits from generics.CreateAPIView to create a standard registration endpoint
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# This view class is for displaying profile information and allowing the owner to modify it
class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]

    # To access the profile based on the user ID
    lookup_field = "user__id"
    lookup_url_kwarg = "user_id"


"""

This class is written for user logout, where we expire the new refresh token.
It is worth mentioning that after login, refresh token rotation is used
so that there is no need to block previous tokens after logout.

"""


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    # Blocking the newest token to cut off access
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Logout was successful"}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"detail": "There has been a problem with logging out"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# This class is for changing the password by the user
class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password Changed"}, status=status.HTTP_200_OK)


# A view class for sending an email for a new user email
class RequestEmailChangeView(generics.GenericAPIView):
    serializer_class = RequestEmailChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "The verification code has been sent to the new email"},
            status=status.HTTP_200_OK,
        )


# Key view for verifying the 6-digit code sent to the new email and saving the new email
class VerifyEmailChangeView(generics.GenericAPIView):
    serializer_class = VerifyEmailChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Your email has been successfully changed"},
            status=status.HTTP_200_OK,
        )


"""

These classes are used for password recovery,
sending a link containing a 6-digit code to the person's email,
and by entering it, they can change their password.


"""


class RequestPasswordResetView(generics.GenericAPIView):
    serializer_class = RequestPasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "The password recovery code has been sent to your email"},
            status=status.HTTP_200_OK,
        )


# Key view for verifying the 6-digit code sent to the user email and saving the new pass
class ConfirmPasswordResetView(generics.GenericAPIView):
    serializer_class = ConfirmPasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Your password has been successfully changed"},
            status=status.HTTP_200_OK,
        )
