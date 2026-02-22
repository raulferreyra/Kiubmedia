from django.shortcuts import render, get_object_or_404
from .models import Post


def post_list(request):
    posts = Post.objects.all().order_by('-pub_date')
    latest_post = posts.first() if posts.exists() else None
    other_posts = posts[1:] if latest_post else posts

    return render(request, 'blog/post_list.html', {
        'posts': other_posts,
        'latest_post': latest_post,
    })
