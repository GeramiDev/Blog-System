from rest_framework import serializers
from blogs.models import BlogPost, Rating


# This class is for serializing the BlogPost model
class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "content",
            "author",
            "created_at",
            "updated_at",
            "total_likes",
            "average_rating",
        ]


# This class is for serializing the Rating model
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id", "score"]
