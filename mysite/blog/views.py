from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import generic
from django.urls import reverse
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import Http404

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        raise Http404("Post does not exist")
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return HttpResponseRedirect(reverse('blog:post_detail', args=(post.id,)))
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return HttpResponseRedirect(reverse('blog:post_detail', args=(post.id,)))
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
    try:
        post = Post.objects.get(pk=pk)
        post.publish()
    except Post.DoesNotExist:
        raise Http404("Post does not exist")
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_remove(request, pk):
    try:
        post = Post.objects.get(pk=pk)
        post.delete()
    except Post.DoesNotExist:
        raise Http404("Post does not exist")
    return HttpResponseRedirect(reverse('blog:post_list'))

#Vistas de comentarios
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse('blog:post_detail', args=(comment.post.id,)))
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return HttpResponseRedirect(reverse('blog:post_detail', args=(comment.post.id,)))

@login_required
def comment_remove(request, pk):
    comment = Comment.objects.get(pk=pk)
    comment.delete()
    return HttpResponseRedirect(reverse('blog:post_detail', args=(comment.post.id,)))
