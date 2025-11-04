from django.urls import path
from .views import CommentCreateListView, CommentDetailView

urlpatterns = [
    path(
        "<int:pk>/comments/", CommentCreateListView.as_view(), name="comment-list"
    ),  # pk = BlogPost Id
    path(
        "comments/<int:pk>/crud/", CommentDetailView.as_view(), name="comment-create"
    ),  # Comment Id
]
