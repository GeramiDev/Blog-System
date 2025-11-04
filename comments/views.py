from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from blogs.permissions import IsAuthorOrReadOnly
from .models import Comments
from blogs.models import BlogPost
from comments.serializer import CommentSerializer
from .permission import IsAuthenticatedOrGuest


# This view class is for creating a new comment for a post
class CommentCreateListView(APIView):

    permission_classes = [IsAuthenticatedOrGuest]

    # Method for listing comments of the desired post
    def get(self, request, pk):
        blog_id = get_object_or_404(BlogPost, pk=pk)
        comment = Comments.objects.filter(blog=blog_id, parent=None).order_by(
            "-created_at"
        )
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Method for creating a comment for the desired post
    def post(self, request, pk):
        blog = get_object_or_404(BlogPost, pk=pk)
        serializer = CommentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(author=request.user, blog=blog)
        return Response(
            CommentSerializer(comment, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


# This class helps the writer change or delete their comment
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]
    """

    Another method has been used to display the user,
    so to avoid any issues, we override the GET method to make it do nothing.

    """

    def get(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            data={"message": "Please change endpoint for Get Comments"},
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Comment Deleted"}, status=status.HTTP_204_NO_CONTENT
        )
