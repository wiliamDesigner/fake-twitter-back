from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [

    path('login/', login_user),

    path(
        'token/',
        TokenObtainPairView.as_view()
    ),

    path(
        'users/create/',
        create_user
    ),

    path(
        'tweets/',
        list_tweets
    ),

    path(
        'tweets/create/',
        create_tweet
    ),

    path(
        'tweets/<int:id>/',
        get_tweet
    ),

    path(
        'tweets/<int:id>/like/',
        like_tweet
    ),

    path(
        'tweets/<int:id>/answers/',
        list_answers
    ),

    path(
        'tweets/<int:tweet_id>/comments/',
        tweet_comments
    ),

    path(
        'follow/<int:id>/',
        follow_user
    ),

    path(
        'feed/',
        get_feed
    ),

    path(
        'users/<int:id>/stats/',
        get_user_stats
    ),

    path(
        'users/update/',
        update_user
    ),

    path(
        'search/',
        search_tweets
    ),

    path(
        'trending/',
        get_trending
    ),

    path(
        'users/<str:username>/',
        get_user_by_username
    ),

    path(
        'avatar/upload/',
        upload_avatar
    ),

    path(
        'cover/upload/',
        upload_cover
    ),

    path(
        'users/',
        list_users
    ),

    path(
        'following/',
        following_list
    ),

    path(
        'users/<int:user_id>/following/',
        user_following
    ),

    path(
    'users/<int:user_id>/followers/',
    user_followers
),

    path(
    "reset-password/",
    reset_password
),

]