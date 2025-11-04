from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Comments
from blogs.models import BlogPost

User = get_user_model()


# This class is for testing operations on comments in the (comments app)
class CommentTests(APITestCase):

    # In this function, we temporarily register and log in once, and create a post to test this program
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="TestUser3", email="Test3@example.com", password="12345!Ab"
        )
        res1 = self.client.post(
            "/api/auth/login/", {"username": "TestUser3", "password": "12345!Ab"}
        )
        token1 = res1.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")
        self.post = BlogPost.objects.create(
            title="Test Post", content="Test Content", author=self.user1
        )

    # Test viewing all comments
    def test_view_comments(self):
        self.client.post(
            f"/api/blogs/{self.post.id}/comments/",
            {"content": "Test Content", "blog": self.post.id},
        )
        response = self.client.get(f"/api/blogs/{self.post.id}/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # If the wrong endpoint is used to view comments, an error should be displayed
    def test_wrong_endpoint_view_comments(self):
        self.client.post(
            f"/api/blogs/{self.post.id}/comments/",
            {"content": "Test Content", "blog": self.post.id},
        )
        response = self.client.get("/api/blogs/comments/1/crud/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Testing posting a comment for a post
    def test_add_comment(self):
        response = self.client.post(
            f"/api/blogs/{self.post.id}/comments/",
            {"content": "Test Content", "blog": self.post.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comments.objects.count(), 1)

    # Testing reply for a comment on a post
    def test_reply_comment(self):
        parent = Comments.objects.create(
            blog=self.post, author=self.user1, content="Test Content"
        )
        response = self.client.post(
            f"/api/blogs/{self.post.id}/comments/",
            {
                "content": "Reply Post Content",
                "parent": parent.id,
                "blog": self.post.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comments.objects.count(), 2)

    # Test deleting comment
    def test_delete_comment(self):
        comment = Comments.objects.create(
            blog=self.post, author=self.user1, content="Test Content"
        )
        response = self.client.delete(f"/api/blogs/comments/{comment.id}/crud/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comments.objects.count(), 0)

    # Testing updating a comment
    def test_update_comment(self):
        comment = Comments.objects.create(
            blog=self.post, author=self.user1, content="Test Content"
        )
        response = self.client.put(
            f"/api/blogs/comments/{comment.id}/crud/",
            {"content": "Updated Content", "blog": self.post.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comments.objects.count(), 1)

    # CRUD operations test for comments for a user other than the author
    def test_other_user_cannot_update_comment(self):
        comment = Comments.objects.create(
            blog=self.post, author=self.user1, content="Test Content"
        )
        self.user2 = User.objects.create_user(
            username="TestUser4", email="Test4@example.com", password="12345!Ab"
        )
        res2 = self.client.post(
            "/api/auth/login/", {"username": "TestUser4", "password": "12345!Ab"}
        )
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        token2 = res2.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")
        response = self.client.put(
            f"/api/blogs/comments/{comment.id}/crud/",
            {"content": "Updated Content", "blog": self.post.id},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
