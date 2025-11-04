from io import BytesIO

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from users.models import Profile, EmailVerification, ForgetPasswordCode
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()


# This class is for testing the (user app) and (authentication)
class UserAuthTests(APITestCase):

    # Registration test and saving it in the database
    def test_auth(self):

        # Register
        res = self.client.post(
            "/api/auth/register/",
            {
                "username": "UserTest1",
                "email": "Test1@gmail.com",
                "password": "123456Ab!",
                "password2": "123456Ab!",
                "first_name": "Test",
                "last_name": "Test",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # login
        response = self.client.post(
            "/api/auth/login/", {"username": "UserTest1", "password": "123456Ab!"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

        # Test access to an endpoint protected with a token
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]
        self.assertTrue(access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        protected_response = self.client.get("/api/blogs/")
        self.assertEqual(protected_response.status_code, status.HTTP_200_OK)

        # logout
        logout_response = self.client.post(
            "/api/auth/logout/", {"refresh": refresh_token}
        )
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        # No access after logout
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh_token}")
        protected_response_after_logout = self.client.post(
            "/api/blogs/", {"title": "Post test", "content": "This is the Test content"}
        )
        self.assertEqual(
            protected_response_after_logout.status_code, status.HTTP_401_UNAUTHORIZED
        )

    # If the passwords do not match during registration, it will give an error
    def test_wrong_password(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "TestPass",
                "email": "TestPass@gmail.com",
                "password": "123456Ab!",
                "password2": "123456Ab!@!",
                "first_name": "Test",
                "last_name": "Test",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # If an email that has already been registered is used during signup, it gives an error
    def test_registered_email(self):
        self.client.post(
            "/api/auth/register/",
            {
                "username": "TestEmail1",
                "email": "email@gmail.com",
                "password": "123456Ab!",
                "password2": "123456Ab!",
                "first_name": "Test",
                "last_name": "Test",
            },
        )
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "TestEmail2",
                "email": "email@gmail.com",
                "password": "123456Ab!",
                "password2": "123456Ab!",
                "first_name": "Test",
                "last_name": "Test",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # If the password is short, an error should be displayed
    def test_password_too_short(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "TestPass",
                "email": "TestPass@gmail.com",
                "password": "12Ab!",
                "password2": "12Ab!",
                "first_name": "Test",
                "last_name": "Test",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # If the password does not contain a number, an error should be displayed
    def test_password_no_number(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "TestPass",
                "email": "TestPass@gmail.com",
                "password": "Abcdefg!",
                "password2": "Abcdefg!",
                "first_name": "Test",
                "last_name": "Test",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # If the password not having at least one uppercase letter, an error should be displayed
    def test_password_no_uppercase_letter(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "TestPass",
                "email": "TestPass@gmail.com",
                "password": "123456ab!",
                "password2": "123456ab!",
                "first_name": "Test",
                "last_name": "Test",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # If the password does not contain one of the characters (!@#$%&*), an error should be displayed
    def test_password_no_char(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "TestPass",
                "email": "TestPass@gmail.com",
                "password": "123456Abc",
                "password2": "123456Abc",
                "first_name": "Test",
                "last_name": "Test",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# This class is for testing profile-related features
class ProfileTests(APITestCase):

    def setUp(self):
        # Creating a user and their related profile
        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="123456!Ab",
            first_name="User",
            last_name="Test",
        )

        # Creating a profile and using get_or_create to prevent UNIQUE error
        self.profile, created = Profile.objects.get_or_create(
            user=self.user, defaults={"bio": "Hello", "avatar": None}
        )

        # Create another user to test access restrictions
        self.other_user = User.objects.create_user(
            username="user1", email="user1@test.com", password="123456!Ab"
        )

        self.url = f"/api/auth/profile/{self.profile.id}/"  # Profile Url

    # Test viewing profile by each user
    def test_view_profile_detail(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("bio", response.data)

    # The profile owner should be able to update their information
    def test_update_own_profile(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        res = self.client.login(username="user", password="123456!Ab")
        data = {
            "first_name": "FirstEdited",
            "last_name": "LastEdited",
            "bio": "Updated Bio",
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "Updated Bio")

    # The user should not be able to change their email
    def test_cannot_update_email_field(self):
        self.client.login(username="user1", password="123456!Ab")
        data = {"email": "newemail@test.com"}
        refresh = RefreshToken.for_user(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.put(self.url, data, format="json")
        self.assertNotEqual(self.user.email, "newemail@test.com")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Another user should not be able to change someone else's personal profile
    def test_other_user_cannot_edit_profile(self):
        self.client.login(username="user1", password="123456!Ab")
        data = {"bio": "I should not edit this"}
        refresh = RefreshToken.for_user(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # If old password is wrong,user can't change password
    def test_change_password_wrong_old(self):
        self.client.login(username="user", password="123456!Ab")
        data = {
            "old_password": "WrongPass",
            "new_password": "12345!Ab",
            "confirm_password": "12345!Ab",
        }
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.put("/api/auth/change-password/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # If passwords are ok,user can change password
    def test_change_password_ok(self):
        self.client.login(username="user", password="123456!Ab")
        data = {
            "old_password": "123456!Ab",
            "new_password": "12345!AB",
            "confirm_password": "12345!AB",
        }
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.put("/api/auth/change-password/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Creating a thumbnail file in memory
    def generate_test_image(self, name="avatar.jpg"):
        file = BytesIO()
        file.write(
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        )
        file.seek(0)
        return SimpleUploadedFile(name, file.read(), content_type="image/jpeg")

    # The user can upload a photo
    def test_upload_avatar(self):
        self.client.login(username="user", password="123456!Ab")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        img = self.generate_test_image("avatar.jpg")
        response = self.client.put(self.url, {"avatar": img}, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertIn("avatars/user_", self.user.profile.avatar.url)
        self.assertNotIn("default.png", self.user.profile.avatar.url)

    # The user can replace their own avatar
    def test_replace_avatar(self):
        self.client.login(username="user", password="123456!Ab")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        img1 = self.generate_test_image("avatar1.jpg")
        self.client.put(self.url, {"avatar": img1}, format="multipart")

        img2 = self.generate_test_image("avatar2.jpg")
        response = self.client.put(self.url, {"avatar": img2}, format="multipart")
        self.assertEqual(response.status_code, 200)

        self.user.profile.refresh_from_db()

        # The new path must be different from the previous one
        self.assertIn("avatars/user_", self.user.profile.avatar.url)
        self.assertNotIn("avatar1.jpg", self.user.profile.avatar.url)

    # The user can delete the photo and the default will be displayed
    def test_remove_avatar(self):
        self.client.login(username="user", password="123456!Ab")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        img = self.generate_test_image("avatar.jpg")
        self.client.put(self.url, {"avatar": img}, format="multipart")

        response = self.client.patch(self.url, {"remove_avatar": True}, format="json")
        self.assertEqual(response.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertIn("default.png", self.user.profile.avatar.url)

    # If the new passwords do not match, it will show an error
    def test_wrong_new_password(self):
        self.client.login(username="user", password="123456!Ab")
        data = {
            "old_password": "123456!Ab",
            "new_password": "12345!AB",
            "confirm_password": "12345!AB@",
        }
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.put("/api/auth/change-password/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# This class is for testing email changes by the user
class EmailChangeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="TUser", password="12345!AB", email="TUser@example.com"
        )
        User.objects.create_user(
            username="AnotherUser", password="12345!Ab", email="new@example.com"
        )

        self.client.login(username="TUser", password="12345!AB")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    # Sending the code to the new email should be successful
    def test_request_email_change_sends_code(self):
        response = self.client.post(
            "/api/auth/email/change/", {"new_email": "newtest@example.com"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            EmailVerification.objects.filter(new_email="newtest@example.com").exists()
        )

    # It should give an error if the email is duplicate
    def test_cannot_use_duplicate_email(self):
        response = self.client.post(
            "/api/auth/email/change/", {"new_email": "new@example.com"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Successful confirmation should change the user's email
    def test_verify_email_change_updates_user_email(self):
        EmailVerification.objects.create(
            user=self.user,
            new_email="new1@example.com",
            code="123456",
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        data = {"new_email": "new1@example.com", "code": "123456"}
        response = self.client.post("/api/auth/email/verify/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new1@example.com")

    # The wrong code should not change the email
    def test_wrong_code_fails(self):
        EmailVerification.objects.create(
            user=self.user,
            new_email="new1@example.com",
            code="654321",
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        data = {"new_email": "new1@example.com", "code": "111111"}
        response = self.client.post("/api/auth/email/verify/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "TUser@example.com")

    # If the user enters the code for a different email during verification, show an error
    def test_wrong_email_in_verify(self):
        EmailVerification.objects.create(
            user=self.user,
            new_email="testing@example.com",
            code="654321",
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        data = {"new_email": "testwrong@example.com", "code": "654321"}
        response = self.client.post("/api/auth/email/verify/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # If a new email has already been registered by another user, show an error
    def test_registered_wrong_new_email(self):
        User.objects.create_user(
            username="reg", password="12345!AB", email="new@email.com"
        )
        EmailVerification.objects.create(
            user=self.user,
            new_email="new@email.com",
            code="123456",
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        data = {"new_email": "new@email.com", "code": "123456"}
        response = self.client.post("/api/auth/email/verify/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # If the code has expired during verification, it shows an error.
    def test_expired_code(self):
        EmailVerification.objects.create(
            user=self.user,
            new_email="test@new.com",
            code="123456",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        data = {"new_email": "test@new.com", "code": "123456"}
        response = self.client.post("/api/auth/email/verify/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# This class is for testing reset password by the user
class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ForgetUser", password="OldPass123!", email="forget@example.com"
        )

    # The password recovery request must generate a code
    def test_request_password_reset_creates_code(self):
        response = self.client.post(
            "/api/auth/forget-password/", {"email": "forget@example.com"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ForgetPasswordCode.objects.filter(user=self.user).exists())

    # With the correct code, the password should be successfully changed
    def test_reset_with_correct_code_changes_password(self):
        code = ForgetPasswordCode.objects.create(
            user=self.user,
            code="123456",
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        data = {
            "email": "forget@example.com",
            "code": "123456",
            "new_password": "NewPass123!",
            "confirm_password": "NewPass123!",
        }
        response = self.client.post("/api/auth/forget-password/change/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass123!"))

    # The wrong code should not change the password
    def test_reset_with_wrong_code_fails(self):
        ForgetPasswordCode.objects.create(
            user=self.user,
            code="999999",
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        data = {
            "email": "forget@example.com",
            "code": "111111",
            "new_password": "NewPass123!",
            "confirm_password": "NewPass123!",
        }
        response = self.client.post("/api/auth/forget-password/change/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OldPass123!"))

    # If the new password and confirmation do not match, it should give an error
    def test_passwords_must_match(self):
        ForgetPasswordCode.objects.create(
            user=self.user,
            code="123456",
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        data = {
            "email": "forget@example.com",
            "code": "123456",
            "new_password": "NewPass123!",
            "confirm_password": "WrongPass1!",
        }
        response = self.client.post("/api/auth/forget-password/change/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
