from rest_framework import serializers
from .models import Comments


# This class is for the serializer, and we have created a custom method for replies
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = ["id", "blog", "author", "content", "parent", "replies", "created_at"]

    # Custom method for replies
    def get_replies(self, obj):
        return CommentSerializer(obj.replies.all(), many=True).data
