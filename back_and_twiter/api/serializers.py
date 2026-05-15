from rest_framework import serializers

from .models import Tweet, Comment


class TweetSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()

    likes = serializers.SerializerMethodField()

    image = serializers.ImageField(required=False)

    class Meta:

        model = Tweet

        fields = [
            'id',
            'content',
            'image',
            'user',
            'likes',
            'created_at'
        ]

    def get_user(self, obj):

        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "avatar": "/emo.jpg"
        }

    def get_likes(self, obj):

        return obj.likes.count()


class CommentSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()

    class Meta:

        model = Comment

        fields = [
            "id",
            "content",
            "created_at",
            "user"
        ]

    def get_user(self, obj):

        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "avatar": "/emo.jpg"
        }


class UpdateUserSerializer(serializers.Serializer):

    name = serializers.CharField(
        min_length=2,
        required=False
    )

    bio = serializers.CharField(
        required=False,
        allow_blank=True
    )

    link = serializers.URLField(
        required=False
    )