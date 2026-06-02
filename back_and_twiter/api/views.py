from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.core.paginator import Paginator
from django.db.models import Count

import re

from .models import (
    Tweet,
    Follow,
    Hashtag,
    Profile,
    TweetLike,
    Comment
)

from .serializers import (
    TweetSerializer,
    CommentSerializer
)


@api_view(['POST'])
def login_user(request):

    username = request.data.get('username')

    password = request.data.get('password')

    print("USERNAME:", username)
    print("PASSWORD:", password)

    if not username or not password:

        return Response({
            "error": "Preencha todos os campos"
        }, status=400)

    try:

        user = User.objects.get(
            username=username
        )

        print("USUÁRIO ENCONTRADO")

    except User.DoesNotExist:

        print("USUÁRIO NÃO EXISTE")

        return Response({
            "error": "Usuário não encontrado"
        }, status=400)

    check = user.check_password(password)

    print("CHECK PASSWORD:", check)

    if not check:

        return Response({
            "error": "Senha inválida"
        }, status=400)

    print("LOGIN OK")

    return Response({
        "user_id": user.id,
        "username": user.username
    })

# CREATE USER
@api_view(['POST'])
def create_user(request):

    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or len(username) < 2:

        return Response({
            "error": "Nome inválido"
        }, status=400)

    if not email or "@" not in email:

        return Response({
            "error": "Email inválido"
        }, status=400)

    if not password or len(password) < 4:

        return Response({
            "error": "Senha muito curta"
        }, status=400)

    if User.objects.filter(username=username).exists():

        return Response({
            "error": "Usuário já existe"
        }, status=400)

    if User.objects.filter(email=email).exists():

        return Response({
            "error": "Email já cadastrado"
        }, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    return Response({
        "id": user.id,
        "username": user.username
    })


# CREATE TWEET
@api_view(['POST'])
def create_tweet(request):

    user_id = request.data.get("user_id")

    content = request.data.get("content", "")

    image = request.FILES.get("image")

    if not content and not image:

        return Response({
            "error": "Content obrigatório"
        }, status=400)

    try:

        user = User.objects.get(id=user_id)

    except User.DoesNotExist:

        return Response({
            "error": "Usuário não encontrado"
        }, status=404)

    tweet = Tweet.objects.create(
        user=user,
        content=content,
        image=image
    )

    hashtags = re.findall(r"#\w+", content)

    for tag in hashtags:

        tag_name = tag.lower()

        hashtag_obj, _ = Hashtag.objects.get_or_create(
            name=tag_name
        )

        tweet.hashtags.add(hashtag_obj)

    serializer = TweetSerializer(tweet)

    return Response(serializer.data)


# LIST TWEETS
@api_view(['GET'])
def list_tweets(request):

    tweets = Tweet.objects.all().order_by('-created_at')

    paginator = Paginator(tweets, 10)

    page = request.GET.get('page', 1)

    page_obj = paginator.get_page(page)

    serializer = TweetSerializer(
        page_obj,
        many=True
    )

    return Response({
        "tweets": serializer.data,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number
    })


# GET TWEET
@api_view(['GET'])
def get_tweet(request, id):

    tweet = Tweet.objects.get(id=id)

    serializer = TweetSerializer(tweet)

    return Response(serializer.data)


# LIKE
@api_view(["POST"])
def like_tweet(request, id):

    try:

        tweet = Tweet.objects.get(id=id)

    except Tweet.DoesNotExist:

        return Response({
            "error": "Tweet não encontrado"
        }, status=404)

    user_id = request.data.get("user_id")

    try:

        user = User.objects.get(id=user_id)

    except User.DoesNotExist:

        return Response({
            "error": "Usuário não encontrado"
        }, status=404)

    like = TweetLike.objects.filter(
        user=user,
        tweet=tweet
    ).first()

    if like:

        like.delete()

        total = TweetLike.objects.filter(
            tweet=tweet
        ).count()

        return Response({
            "liked": False,
            "likes": total
        })

    TweetLike.objects.create(
        user=user,
        tweet=tweet
    )

    total = TweetLike.objects.filter(
        tweet=tweet
    ).count()

    return Response({
        "liked": True,
        "likes": total
    })


# ANSWERS
@api_view(['GET'])
def list_answers(request, id):

    replies = Tweet.objects.filter(
        parent_id=id
    ).order_by('-created_at')

    serializer = TweetSerializer(
        replies,
        many=True
    )

    return Response(serializer.data)


# FOLLOW
@api_view(['POST'])
def follow_user(request, id):

    follower = User.objects.get(
        id=request.data.get('user_id')
    )

    following = User.objects.get(id=id)

    relation = Follow.objects.filter(
        follower=follower,
        following=following
    )

    if relation.exists():

        relation.delete()

        return Response({
            "following": False
        })

    else:

        Follow.objects.create(
            follower=follower,
            following=following
        )

        return Response({
            "following": True
        })


# FEED
@api_view(['GET'])
def get_feed(request):

    user_id = request.GET.get('user_id')

    page = request.GET.get('page', 1)

    following_ids = Follow.objects.filter(
        follower_id=user_id
    ).values_list('following_id', flat=True)

    ids = list(following_ids)

    if user_id:
        ids.append(int(user_id))

    tweets = Tweet.objects.filter(
        user_id__in=ids
    ).order_by('-created_at')

    paginator = Paginator(tweets, 10)

    page_obj = paginator.get_page(page)

    serializer = TweetSerializer(
        page_obj,
        many=True
    )

    return Response({
        "tweets": serializer.data,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number
    })


# USER STATS
@api_view(['GET'])
def get_user_stats(request, id):

    user = User.objects.get(id=id)

    return Response({
        "user_id": user.id,
        "followers": user.followers.count(),
        "following": user.following.count(),
        "tweets": user.tweets.count()
    })


# USER TWEETS
@api_view(['GET'])
def get_user_tweets(request, id):

    tweets = Tweet.objects.filter(
        user_id=id
    ).order_by('-created_at')

    page = request.GET.get('page', 1)

    paginator = Paginator(tweets, 5)

    page_obj = paginator.get_page(page)

    serializer = TweetSerializer(
        page_obj,
        many=True
    )

    return Response({
        "tweets": serializer.data,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number
    })


# UPDATE USER
@api_view(['POST'])
def update_user(request):

    user_id = request.data.get('user_id')

    try:

        user = User.objects.get(id=user_id)

    except User.DoesNotExist:

        return Response({
            "error": "Usuário não encontrado"
        }, status=404)

    username = request.data.get('username')

    email = request.data.get('email')

    if username:

        user.username = username

    if email:

        user.email = email

    user.save()

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email
    })


# COMMENTS
@api_view(["GET", "POST"])
def tweet_comments(request, tweet_id):

    try:

        tweet = Tweet.objects.get(id=tweet_id)

    except Tweet.DoesNotExist:

        return Response({
            "error": "Tweet não encontrado"
        }, status=404)

    if request.method == "GET":

        comments = Comment.objects.filter(
            tweet=tweet
        ).order_by("-created_at")

        serializer = CommentSerializer(
            comments,
            many=True
        )

        return Response(serializer.data)

    if request.method == "POST":

        user_id = request.data.get("user_id")

        content = request.data.get("content")

        user = User.objects.get(id=user_id)

        comment = Comment.objects.create(
            user=user,
            tweet=tweet,
            content=content
        )

        serializer = CommentSerializer(comment)

        return Response(serializer.data)


# FOLLOWING
@api_view(['GET'])
def user_following(request, user_id):

    follows = Follow.objects.filter(
        follower_id=user_id
    )

    data = []

    for follow in follows:

        followed_user = follow.following

        avatar = None

        try:

            if followed_user.profile.avatar:
                avatar = followed_user.profile.avatar.url

        except:
            pass

        data.append({
            "id": followed_user.id,
            "username": followed_user.username,
            "avatar": avatar
        })

    return Response(data)


# FOLLOWERS
@api_view(['GET'])
def user_followers(request, user_id):

    follows = Follow.objects.filter(
        following_id=user_id
    )

    data = []

    for follow in follows:

        follower_user = follow.follower

        avatar = None

        try:

            if follower_user.profile.avatar:
                avatar = follower_user.profile.avatar.url

        except:
            pass

        data.append({
            "id": follower_user.id,
            "username": follower_user.username,
            "avatar": avatar
        })

    return Response(data)


# SEARCH
@api_view(['GET'])
def search_tweets(request):

    query = request.GET.get('q')

    page = int(request.GET.get('page', 0))

    limit = 5

    tweets = Tweet.objects.filter(
        content__icontains=query
    ).order_by('-created_at')

    start = page * limit

    end = start + limit

    tweets = tweets[start:end]

    serializer = TweetSerializer(
        tweets,
        many=True
    )

    return Response(serializer.data)


# TRENDING
@api_view(['GET'])
def get_trending(request):

    trends = Hashtag.objects.annotate(
        total=Count('tweet')
    ).order_by('-total')[:5]

    data = []

    for tag in trends:

        data.append({
            "hashtag": tag.name,
            "count": tag.total
        })

    return Response(data)


# GET USERNAME
@api_view(['GET'])
def get_user_by_username(request, username):

    try:

        user = User.objects.get(
            username__iexact=username
        )

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })

    except User.DoesNotExist:

        return Response({
            "error": "Usuário não existe"
        }, status=404)


# AVATAR
@api_view(["POST"])
def upload_avatar(request):

    user_id = request.data.get("user_id")

    avatar = request.FILES.get("avatar")

    try:

        user = User.objects.get(id=user_id)

        profile, created = Profile.objects.get_or_create(
            user=user
        )

        profile.avatar = avatar

        profile.save()

        return Response({
            "avatar": profile.avatar.url
        })

    except User.DoesNotExist:

        return Response({
            "error": "Usuário não encontrado"
        }, status=404)


# COVER
@api_view(["POST"])
def upload_cover(request):

    user_id = request.data.get("user_id")

    cover = request.FILES.get("cover")

    try:

        user = User.objects.get(id=user_id)

        profile, created = Profile.objects.get_or_create(
            user=user
        )

        profile.cover = cover

        profile.save()

        return Response({
            "cover": profile.cover.url
        })

    except User.DoesNotExist:

        return Response({
            "error": "Usuário não encontrado"
        }, status=404)


# USERS
@api_view(['GET'])
def list_users(request):

    users = User.objects.all()

    data = []

    for user in users:

        data.append({
            "id": user.id,
            "username": user.username
        })

    return Response(data)


# FOLLOWING LIST
@api_view(['GET'])
def following_list(request):

    user_id = request.GET.get("user_id")

    follows = Follow.objects.filter(
        follower_id=user_id
    )

    data = []

    for follow in follows:

        data.append({
            "id": follow.following.id
        })

    return Response(data)


from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.core.paginator import Paginator
from django.db.models import Count

import re

from .models import (
    Tweet,
    Follow,
    Hashtag,
    Profile,
    TweetLike,
    Comment
)

from .serializers import (
    TweetSerializer,
    CommentSerializer
)


# LOGIN
@api_view(['POST'])
def login_user(request):

    user = authenticate(
        username=request.data.get('username'),
        password=request.data.get('password')
    )

    if user:

        return Response({
            "user_id": user.id,
            "username": user.username
        })

    return Response({
        "error": "login inválido"
    }, status=400)


# CREATE USER
@api_view(['POST'])
def create_user(request):

    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or len(username) < 2:

        return Response({
            "error": "Nome inválido"
        }, status=400)

    if not email or "@" not in email:

        return Response({
            "error": "Email inválido"
        }, status=400)

    if not password or len(password) < 4:

        return Response({
            "error": "Senha muito curta"
        }, status=400)

    if User.objects.filter(username=username).exists():

        return Response({
            "error": "Usuário já existe"
        }, status=400)

    if User.objects.filter(email=email).exists():

        return Response({
            "error": "Email já cadastrado"
        }, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    return Response({
        "id": user.id,
        "username": user.username
    })


# CREATE TWEET
@api_view(['POST'])
def create_tweet(request):

    user_id = request.data.get("user_id")

    content = request.data.get("content", "")

    image = request.FILES.get("image")

    if not content and not image:

        return Response({
            "error": "Content obrigatório"
        }, status=400)

    try:

        user = User.objects.get(id=user_id)

    except User.DoesNotExist:

        return Response({
            "error": "Usuário não encontrado"
        }, status=404)

    tweet = Tweet.objects.create(
        user=user,
        content=content,
        image=image
    )

    hashtags = re.findall(r"#\w+", content)

    for tag in hashtags:

        tag_name = tag.lower()

        hashtag_obj, _ = Hashtag.objects.get_or_create(
            name=tag_name
        )

        tweet.hashtags.add(hashtag_obj)

    serializer = TweetSerializer(tweet)

    return Response(serializer.data)


# LIST TWEETS
@api_view(['GET'])
def list_tweets(request):

    tweets = Tweet.objects.all().order_by('-created_at')

    paginator = Paginator(tweets, 10)

    page = request.GET.get('page', 1)

    page_obj = paginator.get_page(page)

    serializer = TweetSerializer(
        page_obj,
        many=True
    )

    return Response({
        "tweets": serializer.data,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number
    })


# GET TWEET
@api_view(['GET'])
def get_tweet(request, id):

    tweet = Tweet.objects.get(id=id)

    serializer = TweetSerializer(tweet)

    return Response(serializer.data)


# LIKE
@api_view(["POST"])
def like_tweet(request, id):

    try:

        tweet = Tweet.objects.get(id=id)

    except Tweet.DoesNotExist:

        return Response({
            "error": "Tweet não encontrado"
        }, status=404)

    user_id = request.data.get("user_id")

    try:

        user = User.objects.get(id=user_id)

    except User.DoesNotExist:

        return Response({
            "error": "Usuário não encontrado"
        }, status=404)

    like = TweetLike.objects.filter(
        user=user,
        tweet=tweet
    ).first()

    if like:

        like.delete()

        total = TweetLike.objects.filter(
            tweet=tweet
        ).count()

        return Response({
            "liked": False,
            "likes": total
        })

    TweetLike.objects.create(
        user=user,
        tweet=tweet
    )

    total = TweetLike.objects.filter(
        tweet=tweet
    ).count()

    return Response({
        "liked": True,
        "likes": total
    })


# ANSWERS
@api_view(['GET'])
def list_answers(request, id):

    replies = Tweet.objects.filter(
        parent_id=id
    ).order_by('-created_at')

    serializer = TweetSerializer(
        replies,
        many=True
    )

    return Response(serializer.data)


# FOLLOW
@api_view(['POST'])
def follow_user(request, id):

    follower = User.objects.get(
        id=request.data.get('user_id')
    )

    following = User.objects.get(id=id)

    relation = Follow.objects.filter(
        follower=follower,
        following=following
    )

    if relation.exists():

        relation.delete()

        return Response({
            "following": False
        })

    else:

        Follow.objects.create(
            follower=follower,
            following=following
        )

        return Response({
            "following": True
        })


# FEED
@api_view(['GET'])
def get_feed(request):

    user_id = request.GET.get('user_id')

    page = request.GET.get('page', 1)

    following_ids = Follow.objects.filter(
        follower_id=user_id
    ).values_list('following_id', flat=True)

    ids = list(following_ids)

    if user_id:
        ids.append(int(user_id))

    tweets = Tweet.objects.filter(
        user_id__in=ids
    ).order_by('-created_at')

    paginator = Paginator(tweets, 10)

    page_obj = paginator.get_page(page)

    serializer = TweetSerializer(
        page_obj,
        many=True
    )

    return Response({
        "tweets": serializer.data,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number
    })


# USER STATS
@api_view(['GET'])
def get_user_stats(request, id):

    user = User.objects.get(id=id)

    return Response({
        "user_id": user.id,
        "followers": user.followers.count(),
        "following": user.following.count(),
        "tweets": user.tweets.count()
    })


# USER TWEETS
@api_view(['GET'])
def get_user_tweets(request, id):

    tweets = Tweet.objects.filter(
        user_id=id
    ).order_by('-created_at')

    page = request.GET.get('page', 1)

    paginator = Paginator(tweets, 5)

    page_obj = paginator.get_page(page)

    serializer = TweetSerializer(
        page_obj,
        many=True
    )

    return Response({
        "tweets": serializer.data,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number
    })


# UPDATE USER
@api_view(['POST'])
def update_user(request):

    user_id = request.data.get('user_id')

    try:

        user = User.objects.get(id=user_id)

    except User.DoesNotExist:

        return Response({
            "error": "Usuário não encontrado"
        }, status=404)

    username = request.data.get('username')

    email = request.data.get('email')

    if username:

        user.username = username

    if email:

        user.email = email

    user.save()

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email
    })


# COMMENTS
@api_view(["GET", "POST"])
def tweet_comments(request, tweet_id):

    try:

        tweet = Tweet.objects.get(id=tweet_id)

    except Tweet.DoesNotExist:

        return Response({
            "error": "Tweet não encontrado"
        }, status=404)

    if request.method == "GET":

        comments = Comment.objects.filter(
            tweet=tweet
        ).order_by("-created_at")

        serializer = CommentSerializer(
            comments,
            many=True
        )

        return Response(serializer.data)

    if request.method == "POST":

        user_id = request.data.get("user_id")

        content = request.data.get("content")

        user = User.objects.get(id=user_id)

        comment = Comment.objects.create(
            user=user,
            tweet=tweet,
            content=content
        )

        serializer = CommentSerializer(comment)

        return Response(serializer.data)


# FOLLOWING
@api_view(['GET'])
def user_following(request, user_id):

    follows = Follow.objects.filter(
        follower_id=user_id
    )

    data = []

    for follow in follows:

        followed_user = follow.following

        avatar = None

        try:

            if followed_user.profile.avatar:
                avatar = followed_user.profile.avatar.url

        except:
            pass

        data.append({
            "id": followed_user.id,
            "username": followed_user.username,
            "avatar": avatar
        })

    return Response(data)


# FOLLOWERS
@api_view(['GET'])
def user_followers(request, user_id):

    follows = Follow.objects.filter(
        following_id=user_id
    )

    data = []

    for follow in follows:

        follower_user = follow.follower

        avatar = None

        try:

            if follower_user.profile.avatar:
                avatar = follower_user.profile.avatar.url

        except:
            pass

        data.append({
            "id": follower_user.id,
            "username": follower_user.username,
            "avatar": avatar
        })

    return Response(data)


# SEARCH
@api_view(['GET'])
def search_tweets(request):

    query = request.GET.get('q')

    page = int(request.GET.get('page', 0))

    limit = 5

    tweets = Tweet.objects.filter(
        content__icontains=query
    ).order_by('-created_at')

    start = page * limit

    end = start + limit

    tweets = tweets[start:end]

    serializer = TweetSerializer(
        tweets,
        many=True
    )

    return Response(serializer.data)


# TRENDING
@api_view(['GET'])
def get_trending(request):

    trends = Hashtag.objects.annotate(
        total=Count('tweet')
    ).order_by('-total')[:5]

    data = []

    for tag in trends:

        data.append({
            "hashtag": tag.name,
            "count": tag.total
        })

    return Response(data)


# GET USERNAME
@api_view(['GET'])
def get_user_by_username(request, username):

    try:

        user = User.objects.get(
            username__iexact=username
        )

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })

    except User.DoesNotExist:

        return Response({
            "error": "Usuário não existe"
        }, status=404)


# AVATAR
@api_view(["POST"])
def upload_avatar(request):

    user_id = request.data.get("user_id")

    avatar = request.FILES.get("avatar")

    try:

        user = User.objects.get(id=user_id)

        profile, created = Profile.objects.get_or_create(
            user=user
        )

        profile.avatar = avatar

        profile.save()

        return Response({
            "avatar": profile.avatar.url
        })

    except User.DoesNotExist:

        return Response({
            "error": "Usuário não encontrado"
        }, status=404)


# COVER
@api_view(["POST"])
def upload_cover(request):

    user_id = request.data.get("user_id")

    cover = request.FILES.get("cover")

    try:

        user = User.objects.get(id=user_id)

        profile, created = Profile.objects.get_or_create(
            user=user
        )

        profile.cover = cover

        profile.save()

        return Response({
            "cover": profile.cover.url
        })

    except User.DoesNotExist:

        return Response({
            "error": "Usuário não encontrado"
        }, status=404)


# USERS
@api_view(['GET'])
def list_users(request):

    users = User.objects.all()

    data = []

    for user in users:

        data.append({
            "id": user.id,
            "username": user.username
        })

    return Response(data)


# FOLLOWING LIST
@api_view(['GET'])
def following_list(request):

    user_id = request.GET.get("user_id")

    follows = Follow.objects.filter(
        follower_id=user_id
    )

    data = []

    for follow in follows:

        data.append({
            "id": follow.following.id
        })

    return Response(data)


@api_view(["POST"])
def reset_password(request):

    username = request.data.get("username")

    email = request.data.get("email")

    password = request.data.get("password")

    print("RESET USERNAME:", username)
    print("RESET EMAIL:", email)
    print("RESET PASSWORD:", password)

    if not username:

        return Response({
            "error": "Nome obrigatório"
        }, status=400)

    if not email:

        return Response({
            "error": "Email obrigatório"
        }, status=400)

    if not password:

        return Response({
            "error": "Senha obrigatória"
        }, status=400)

    try:

        user = User.objects.get(
            username=username,
            email=email
        )

        print("USUÁRIO RESET ENCONTRADO")

    except User.DoesNotExist:

        print("USUÁRIO RESET NÃO EXISTE")

        return Response({
            "error": "Nome ou email inválido"
        }, status=404)

    user.set_password(password)

    user.save()

    print("SENHA ALTERADA")

    return Response({
        "success": True,
        "message": "Senha alterada com sucesso"
    })