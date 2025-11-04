from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from datetime import timedelta
from django.utils import timezone


# Create a model based on a Django class that has the main fields for the user
class User(AbstractUser):

    username = models.CharField(
        max_length=20,
        unique=True,
        blank=False,
        null=False,
        help_text=(
            "Required. 20 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
    )
    password = models.CharField(
        help_text="The password must include at least 8 characters,"
        " one number, one uppercase letter,"
        " and a special character (!@#$%&*)."
    )
    email = models.EmailField(blank=False, null=False, unique=True)


# َAvatar path for profile
def avatar_upload_path(instance, filename):
    if not instance.id:
        instance.save()
    return f"avatars/user_{instance.id}/{filename}"


"""

This model is for user profiles,
where the settings configured for 
this user set are stored as a record in this model after registration.

"""


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True, null=True, default="This is a bio about me")
    avatar = models.ImageField(
        blank=True,
        null=True,
        upload_to=avatar_upload_path,
        default="avatars/default.png",
    )


# Signal for automatic profile creation after registration
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# This model is for email authentication and updating it with a random 6-digit code
class EmailVerification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="email_verifications"
    )
    new_email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Generate a random 6-digit code fro 5 minutes
    def generate_code(self):
        self.code = str(random.randint(100000, 999999))
        self.expires_at = timezone.now() + timedelta(minutes=5)
        self.save()

    def is_expired(self):
        return timezone.now() > self.expires_at


# This model is for email authentication and reset password with a random 6-digit code
class ForgetPasswordCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_codes")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Generate a random 6-digit code fro 5 minutes
    def generate_code(self):
        self.code = str(random.randint(100000, 999999))
        self.expires_at = timezone.now() + timedelta(minutes=5)
        self.save()

    def is_expired(self):
        return timezone.now() > self.expires_at
