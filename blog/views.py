from django.shortcuts import render, get_object_or_404
from .models import Post


def post_list(request):
    published_posts = Post.objects.filter(
        status='published').order_by('-pub_date')
    latest_post = published_posts.first() if published_posts.exists() else None
    other_posts = published_posts[1:] if latest_post else published_posts

    return render(request, 'blog/post_list.html', {
        'posts': other_posts,
        'latest_post': latest_post,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    related_posts = post.get_related_posts()
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'related_posts': related_posts,
    })
