from django.db import models
from django.contrib.auth.models  import User


class Profile(models.Model):

        user = models.OneToOneField(
            User,
            on_delete=models.CASCADE
        )

        avatar = models.ImageField(
            upload_to="avatars/",
            blank=True,
            null=True
        )

        cover = models.ImageField(
            upload_to="covers/",
            blank=True,
            null=True
        )

        bio = models.TextField(
            blank=True,
            null=True
        )

        def __str__(self):
            return self.user.username


class Hashtag(models.Model):

        name = models.CharField(
            max_length=100,
            unique=True
        )

        def __str__(self):
            return self.name


class Tweet(models.Model):

        user = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='tweets'
        )

        content = models.TextField(
            blank=True,
            null=True
        )

        # IMAGEM DO TWEET
        image = models.ImageField(
            upload_to="tweets/",
            blank=True,
            null=True
        )

        parent = models.ForeignKey(
            'self',
            null=True,
            blank=True,
            on_delete=models.CASCADE,
            related_name='replies'
        )

        created_at = models.DateTimeField(
            auto_now_add=True
        )

        hashtags = models.ManyToManyField(
            Hashtag,
            blank=True
        )

        def __str__(self):
            return f"{self.user.username}: {self.content[:30]}"


class TweetLike(models.Model):

        user = models.ForeignKey(
            User,
            on_delete=models.CASCADE
        )

        tweet = models.ForeignKey(
            Tweet,
            on_delete=models.CASCADE,
            related_name='likes'
        )

        class Meta:
            unique_together = ('user', 'tweet')


class Follow(models.Model):

        follower = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='following'
        )

        following = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='followers'
        )

        class Meta:
            unique_together = ('follower', 'following')


class Comment(models.Model):

        user = models.ForeignKey(
            User,
            on_delete=models.CASCADE
        )

        tweet = models.ForeignKey(
            Tweet,
            on_delete=models.CASCADE,
            related_name="comments"
        )

        content = models.TextField()

        created_at = models.DateTimeField(
            auto_now_add=True
        )

        def __str__(self):

            return self.content