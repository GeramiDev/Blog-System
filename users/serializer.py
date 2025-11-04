from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from users.models import Profile, EmailVerification, ForgetPasswordCode

# Creating access to the model in this module
User = get_user_model()


# This class is for the serializer of registration activities
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Confirm Password")

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
        )

    # Checking whether the user is using the password they set or not
    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    # Checking that this email has not been registered before
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email has already been registered.")
        return value

    # If qualified, the user's information will be saved in the relevant table.
    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email"),
            last_name=validated_data.get("last_name", ""),
            first_name=validated_data.get("first_name", ""),
        )
        return user


"""

This class is for the user profile serializer
Note: If in the future there is a need for development using
email change with authentication,
the parameter read_only=True should be removed.

Fields that are read from the user model:

"""


class ProfileSerializer(serializers.ModelSerializer):

    # Fields that are read from the user model
    email = serializers.ReadOnlyField(
        source="user.email", read_only=True
    )  # It cannot be changed for now
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    remove_avatar = serializers.BooleanField(
        write_only=True, required=False, default=False
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "bio",
            "avatar",
            "remove_avatar",
        ]

    def update(self, instance, validated_data):

        # Updating User Model Fields
        user_data = validated_data.pop("user", {})
        if "first_name" in user_data:
            instance.user.first_name = user_data["first_name"]
        if "last_name" in user_data:
            instance.user.last_name = user_data["last_name"]

        instance.user.save()

        default_avatar_path = "avatars/default.png"  # Your default photo path

        # Delete avatar
        if validated_data.get("remove_avatar", False):
            if instance.avatar and instance.avatar.name != default_avatar_path:
                instance.avatar.delete(save=False)
            instance.avatar = default_avatar_path
            instance.save()
            return instance

        # Update avatar
        new_avatar = validated_data.get("avatar", None)
        if new_avatar:
            # If an avatar already exists for the user, it will delete it and replace it with the new avatar
            old_avatar = instance.avatar
            if (
                old_avatar
                and old_avatar.name != new_avatar.name
                and old_avatar.name != default_avatar_path
            ):
                old_avatar.delete(save=False)
            instance.avatar = new_avatar

        # Update your profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# This serializer is for checking old password and validate new password and finally save it for user
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True, label="Old Password", required=True
    )
    new_password = serializers.CharField(
        write_only=True,
        label="New Password",
        validators=[validate_password],
        required=True,
    )
    confirm_password = serializers.CharField(
        write_only=True, label="Confirm Password", required=True
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Enter your old password correctly")
        return value

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("New Passwords don't match")
        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


"""

Checking and creating a new record under the username
and sending an email with the code upon approval

"""


class RequestEmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField()

    def validate_new_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email has already been registered")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        new_email = self.validated_data["new_email"]

        # If a code was previously registered for this user, update that one
        verification, _ = EmailVerification.objects.update_or_create(
            user=user,
            new_email=new_email,
            is_verified=False,
            defaults={"expires_at": None},
        )

        verification.generate_code()  # Generate new code and set expiration

        # Send Email
        send_mail(
            subject="Email change verification code",
            message=f"Your verification code: {verification.code}",
            from_email="no-reply@example.com",
            recipient_list=[new_email],
            fail_silently=False,
        )

        return verification


# Verify the code and save the new email in the user model
class VerifyEmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        user = self.context["request"].user
        try:
            verification = EmailVerification.objects.get(
                user=user, new_email=data["new_email"], is_verified=False
            )
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("No request was found for this email")

        if User.objects.filter(email=data["new_email"]).exclude(pk=user.pk).exists():
            raise serializers.ValidationError(
                "This email is already registered for another user"
            )

        if verification.is_expired():
            raise serializers.ValidationError(
                "The code has expired, please request it again"
            )

        if verification.code != data["code"]:
            raise serializers.ValidationError("The entered code is incorrect.")

        return data

    def save(self, **kwargs):
        user = self.context["request"].user

        verification = EmailVerification.objects.get(
            user=user,
            new_email=self.validated_data["new_email"],
            code=self.validated_data["code"],
        )

        # Confirm new email
        verification.is_verified = True
        verification.save()

        # Update user email
        user.email = self.validated_data["new_email"]
        user.save()

        return user


"""

Checked for the existence of a user with the entered email
and sent an email containing a 6-digit code for verification

"""


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user was found with this email")
        return value

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data["email"])
        reset_obj, created = ForgetPasswordCode.objects.update_or_create(
            user=user, is_verified=False, defaults={"expires_at": None}
        )
        reset_obj.generate_code()

        # Send email
        send_mail(
            subject="Password reset verification code",
            message=f"Your verification code: {reset_obj.code}",
            from_email="no-reply@example.com",
            recipient_list=[user.email],
            fail_silently=False,
        )
        return reset_obj


# Verify the code and save the new password in the user model
class ConfirmPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = User.objects.get(email=data["email"])
        verification = ForgetPasswordCode.objects.get(user=user, is_verified=False)
        if verification.is_expired():
            raise serializers.ValidationError(
                "The code has expired, please request it again"
            )
        if verification.code != data["code"]:
            raise serializers.ValidationError("The entered code is incorrect.")

        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("The new passwords do not match")

        return data

    def save(self, **kwargs):
        email = self.validated_data["email"]
        code = self.validated_data["code"]
        new_password = self.validated_data["new_password"]
        user = User.objects.get(email=email)
        reset_obj = ForgetPasswordCode.objects.get(
            user=user, code=code, is_verified=False
        )

        # Verified email
        reset_obj.is_verified = True
        reset_obj.save()

        # Change Password
        user.set_password(new_password)
        user.save()

        return user
