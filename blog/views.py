from django.shortcuts import render, get_object_or_404
from blog.models import Post, Tag


def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        "first_tag_title": post.tags.first().title,
    }


def serialize_tag(tag):
    return {
        "title": tag.title,
        "posts_with_tag": tag.posts_count,
    }


def detalize_post(post):
    comments = post.comments.select_related("author")
    serialized_comments = []
    for comment in comments:
        serialized_comments.append(
            {
                "text": comment.text,
                "published_at": comment.published_at,
                "author": comment.author.username,
            }
        )

    related_tags = post.tags.count_posts()

    detalized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author,
        "comments": serialized_comments,
        "likes_amount": post.likes_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in related_tags],
    }

    return detalized_post


def index(request):
    all_posts = Post.objects.prefetch_parameters().count_likes()

    most_popular_posts = all_posts.order_by("-likes_count")[:5]
    most_popular_posts.count_comments()

    most_fresh_posts = all_posts.order_by("-published_at")[:5]
    most_fresh_posts.count_comments()

    most_popular_tags = Tag.objects.count_posts().order_by("-posts_count")[:5]

    context = {
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
        "page_posts": [serialize_post(post) for post in most_fresh_posts],
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, "index.html", context)


def post_detail(request, slug):
    all_posts = Post.objects.prefetch_parameters().count_likes()
    post = get_object_or_404(all_posts, slug=slug)

    most_popular_posts = all_posts.order_by("-likes_count")[:5]
    most_popular_posts.count_comments()

    most_popular_tags = Tag.objects.count_posts().order_by("-posts_count")[:5]

    context = {
        "post": detalize_post(post),
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):
    all_posts = Post.objects.prefetch_parameters().count_likes()
    tag = get_object_or_404(Tag, title=tag_title)

    most_popular_posts = all_posts.order_by("-likes_count")[:5]
    most_popular_posts.count_comments()

    most_popular_tags = Tag.objects.count_posts().order_by("-posts_count")[:5]

    related_posts = tag.posts.count_tags()[:10]
    related_posts.count_comments()

    context = {
        "tag": tag.title,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "posts": [serialize_post(post) for post in related_posts],
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, "posts-list.html", context)


def contacts(request):
    return render(request, "contacts.html", {})
