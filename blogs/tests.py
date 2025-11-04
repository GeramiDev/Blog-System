from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import BlogPost, Rating

User = get_user_model()


# This class is for testing operations on posts in the (blogs app)
class BlogTest(APITestCase):

    # In this function, we temporarily register and log in once for testing this app
    def setUp(self):
        self.user = User.objects.create_user(
            username="TestUser2", email="Test2@gmail.com", password="123456!Ab"
        )
        res = self.client.post(
            "/api/auth/login/", {"username": "TestUser2", "password": "123456!Ab"}
        )
        self.token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    # Test Blog post creation by the author
    def test_create_post(self):
        response = self.client.post(
            "/api/blogs/", {"title": "Test title", "content": "Test content"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlogPost.objects.count(), 1)

    # TTest deleting blog post
    def test_delete_post(self):
        post = BlogPost.objects.create(
            title="Old title", content="Old content", author=self.user
        )
        response = self.client.delete(f"/api/blogs/{post.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test of editing or deleting a post by the author
    def test_edit_post_by_author(self):
        post = BlogPost.objects.create(
            title="Old title", content="Old content", author=self.user
        )
        response = self.client.put(
            f"/api/blogs/{post.id}/", {"title": "New title", "content": "New title"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, "New title")

    def test_edit_post_by_other_user(self):
        post = BlogPost.objects.create(
            title="Old title", content="Old content", author=self.user
        )
        self.user2 = User.objects.create_user(
            username="OtherUser", email="other@example.com", password="12345!Ab"
        )
        res = self.client.post(
            "/api/auth/login/", {"username": "OtherUser", "password": "12345!Ab"}
        )
        self.token2 = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token2}")

        response = self.client.put(
            f"/api/blogs/{post.id}/", {"title": "New title2", "content": "New title2"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        post.refresh_from_db()
        self.assertEqual(post.title, "Old title")

    # Testing liking a post
    def test_like_post(self):
        post = BlogPost.objects.create(
            title="Test title", content="Test content", author=self.user
        )
        response = self.client.post(f"/api/blogs/{post.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(post.likes.count(), 1)

    # Post rating test
    def test_rate_post(self):
        post = BlogPost.objects.create(
            title="Test title", content="Test content", author=self.user
        )
        response = self.client.post(f"/api/blogs/{post.id}/rate/", {"score": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(post.ratings.first().score, 5)

    # Testing unliking a post
    def test_unlike_post(self):
        post = BlogPost.objects.create(
            title="Test title", content="Test content", author=self.user
        )
        self.client.post(f"/api/blogs/{post.id}/like/")
        response = self.client.post(f"/api/blogs/{post.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Numeric test excluding 1 to 5 in scoring
    def test_wrong_rate_post(self):
        post = BlogPost.objects.create(
            title="Test title", content="Test content", author=self.user
        )
        response = self.client.post(f"/api/blogs/{post.id}/rate/", {"score": 7})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test calculation of the average score of each post
    def test_average_rating_returns_correct_value(self):
        post = BlogPost.objects.create(
            title="Test title", content="Test content", author=self.user
        )
        self.client.post(f"/api/blogs/{post.id}/rate/", {"score": 5})

        User.objects.create_user(
            username="otheruser", email="other2@example.com", password="12345!Ab"
        )
        res = self.client.post(
            "/api/auth/login/", {"username": "otheruser", "password": "12345!Ab"}
        )
        self.token3 = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token3}")

        self.client.post(f"/api/blogs/{post.id}/rate/", {"score": 3})
        avg = BlogPost.average_rating(post)
        self.assertEqual(avg, 4.0)

    # If it doesn't have an average and has no score
    def test_average_rating_returns_none_if_no_ratings(self):
        post = BlogPost.objects.create(
            title="Test title", content="Test content", author=self.user
        )
        avg = BlogPost.average_rating(post)
        self.assertIsNone(avg)
