from django.shortcuts import render, get_object_or_404
from .models import Post


def home(request):
    return render(request, 'blog/home.html')

def post_list(request):
    posts = Post.objects.all().order_by('-date_created')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'blog/post_detail.html', {'post': post})