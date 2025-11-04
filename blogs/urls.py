from django.urls import path
from .views import (
    BlogPostDetailView,
    BlogPostRateView,
    BlogPostLikeView,
    BlogPostListCreateView,
)

urlpatterns = [
    path("", BlogPostListCreateView.as_view(), name="blog-list-create"),
    path("<int:pk>/", BlogPostDetailView.as_view(), name="blog-detail"),
    path("<int:pk>/like/", BlogPostLikeView.as_view(), name="blog-like"),
    path("<int:pk>/rate/", BlogPostRateView.as_view(), name="blog-rate"),
]
