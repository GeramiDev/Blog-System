from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsAuthorOrReadOnly
from blogs.models import BlogPost, Rating
from blogs.serializer import BlogPostSerializer

"""

This class is for viewing posts and,
upon command 'Post' and successful authentication,
creates a record in the BlogPost table.

"""


class BlogPostListCreateView(generics.ListCreateAPIView):
    queryset = BlogPost.objects.all().order_by("-created_at")
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Creates a record in the BlogPost table
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# This class helps the author edit or delete the post
class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Blog Post Deleted"}, status=status.HTTP_200_OK)


# This class is for performing like and dislike operations
class BlogPostLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        blog = get_object_or_404(BlogPost, pk=pk)
        if request.user in blog.likes.all():
            blog.likes.remove(request.user)
            return Response({"message": "Unliked"}, status=status.HTTP_200_OK)
        else:
            blog.likes.add(request.user)
            return Response({"message": "Liked"}, status=status.HTTP_200_OK)


# This class is for recording the rating for each post in the Rating table
class BlogPostRateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        blog = get_object_or_404(BlogPost, pk=pk)
        score = request.data.get("score")
        if not score or int(score) not in [1, 2, 3, 4, 5]:
            return Response(
                {"message": "Score must be between 1 and 5"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating, created = Rating.objects.update_or_create(
            user=request.user, blog=blog, defaults={"score": score}
        )
        return Response(
            {"message": "Rating saved", "score": rating.score},
            status=status.HTTP_200_OK,
        )
