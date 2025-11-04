from django.db import models
from django.conf import settings


# Creating a custom model with the required fields for each blog post
class BlogPost(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True
    )

    def total_likes(self):
        return self.likes.count()

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.score for r in ratings) / ratings.count(), 2)
        return None

    def __str__(self):
        return self.title


# Creating a model for the scores of each post by users, which is linked to other models through the primary key
class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="ratings")
    score = models.IntegerField()

    class Meta:
        unique_together = ("user", "blog")

    def __str__(self):
        return f"User {self.user.username} gave a score of {self.score} to {self.blog.title}'s post"
