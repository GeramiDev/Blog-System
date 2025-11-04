from django.urls import path
from .views import (
    RegisterView,
    LogoutView,
    ProfileDetailView,
    ChangePasswordView,
    RequestEmailChangeView,
    VerifyEmailChangeView,
    RequestPasswordResetView,
    ConfirmPasswordResetView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/<int:user_id>/", ProfileDetailView.as_view(), name="user-profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path(
        "email/change/", RequestEmailChangeView.as_view(), name="request-email-change"
    ),
    path("email/verify/", VerifyEmailChangeView.as_view(), name="verify-email-change"),
    path(
        "forget-password/", RequestPasswordResetView.as_view(), name="forget-password"
    ),
    path(
        "forget-password/change/",
        ConfirmPasswordResetView.as_view(),
        name="reset-password",
    ),
]
