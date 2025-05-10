from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Post, Category, Tag, Comment, UserProfile
from .forms import (PostForm, CommentForm, CustomUserCreationForm, 
                   CustomAuthenticationForm, UserProfileForm, CategoryForm, SearchForm)
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from .serializers import PostSerializer, CategorySerializer, TagSerializer, CommentSerializer, UserProfileSerializer


# Home Page
def home(request):
    featured_posts = Post.objects.filter(status='published').order_by('-views')[:5]
    recent_posts = Post.objects.filter(status='published').order_by('-date_created')[:5]
    categories = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:10]
    popular_tags = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:15]
    
    context = {
        'featured_posts': featured_posts,
        'recent_posts': recent_posts,
        'categories': categories,
        'popular_tags': popular_tags,
    }
    return render(request, 'blog/home.html', context)


# Post List View
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Post.objects.filter(status='published').order_by('-date_created')
        
        # Filter by category if provided
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by tag if provided
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
            
        # Search functionality
        search_form = SearchForm(self.request.GET)
        if search_form.is_valid() and search_form.cleaned_data['query']:
            query = search_form.cleaned_data['query']
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) | 
                Q(excerpt__icontains=query) |
                Q(author__username__icontains=query) |
                Q(category__name__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm(self.request.GET)
        context['categories'] = Category.objects.annotate(post_count=Count('posts'))
        context['popular_tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
        
        # Add category or tag info if filtering
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)
            
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            context['current_tag'] = get_object_or_404(Tag, slug=tag_slug)
            
        return context


# Post Detail View
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'
    
    def get_object(self):
        post = super().get_object()
        # Increment view count
        post.views += 1
        post.save()
        return post
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        
        # Add comments
        comments = post.comments.filter(parent=None).order_by('-date_created')
        context['comments'] = comments
        context['comment_form'] = CommentForm()
        
        # Check if user has liked the post
        if self.request.user.is_authenticated:
            context['user_has_liked'] = post.likes.filter(id=self.request.user.id).exists()
        
        # Related posts (same category or tags)
        related_posts = Post.objects.filter(status='published')
        if post.category:
            related_posts = related_posts.filter(category=post.category)
        else:
            related_posts = related_posts.filter(tags__in=post.tags.all())
            
        related_posts = related_posts.exclude(id=post.id).distinct()[:3]
        context['related_posts'] = related_posts
        
        return context
    

# Post Create View
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create_post.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)
    

# Post Update View
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/update_post.html'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)
    

# Post Delete View
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/delete_post.html'
    success_url = reverse_lazy('post_list')
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Post deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Comment functionality
@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            # Check if it's a reply
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, id=parent_id)
                
            comment.save()
            messages.success(request, 'Your comment has been added!')
            
    return redirect('post_detail', slug=post.slug)


# Like functionality
@login_required
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        
    if request.is_ajax():
        return JsonResponse({'liked': liked, 'count': post.total_likes()})
    
    return redirect('post_detail', slug=post.slug)


# User Registration
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        # Check if terms checkbox is checked
        terms_accepted = request.POST.get('terms', False)
        
        if form.is_valid():
            if not terms_accepted:
                # Add terms error to the form's non_field_errors
                form.add_error(None, 'You must accept the Terms of Service and Privacy Policy to register.')
                return render(request, 'blog/register.html', {'form': form, 'terms_error': True})
                
            # Save the user
            user = form.save()
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Log the user in
            # Use authenticate before login to ensure proper backend processing
            authenticated_user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            if authenticated_user is not None:
                login(request, authenticated_user)
            
            # Add success message
            messages.success(request, f'Account created for {user.username}! Welcome to PyBlog!')
            
            # Redirect to home page
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'blog/register.html', {'form': form})


# User Login
def user_login(request):
    # If user is already authenticated, redirect to home
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                # Redirect to next URL if provided, otherwise home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                # This should not normally happen as form validation should catch this
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
        
    return render(request, 'blog/login.html', {'form': form})


# User Logout
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# User Profile
@login_required
def profile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
        
    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get user's posts
    posts = Post.objects.filter(author=user).order_by('-date_created')
    
    context = {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
    }
    
    return render(request, 'blog/profile.html', context)


# Edit Profile
@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
        
    return render(request, 'blog/edit_profile.html', {'form': form})


# Category List
def category_list(request):
    categories = Category.objects.annotate(post_count=Count('posts')).order_by('name')
    return render(request, 'blog/category_list.html', {'categories': categories})


# Tag List
def tag_list(request):
    tags = Tag.objects.annotate(post_count=Count('posts')).order_by('name')
    return render(request, 'blog/tag_list.html', {'tags': tags})


# Dashboard for authenticated users
@login_required
def dashboard(request):
    user_posts = Post.objects.filter(author=request.user).order_by('-date_created')
    draft_posts = user_posts.filter(status='draft')
    published_posts = user_posts.filter(status='published')
    
    context = {
        'user_posts': user_posts,
        'draft_posts': draft_posts,
        'published_posts': published_posts,
        'post_count': user_posts.count(),
        'draft_count': draft_posts.count(),
        'published_count': published_posts.count(),
    }
    
    return render(request, 'blog/dashboard.html', context)


# API Views
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


@api_view(['GET'])
def post_list_api(request):
    posts = Post.objects.filter(status='published')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def post_detail_api(request, slug):
    try:
        post = Post.objects.get(slug=slug)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def post_create_api(request):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def post_update_api(request, slug):
    try:
        post = Post.objects.get(slug=slug)
        
        # Check if user is author or staff
        if request.user != post.author and not request.user.is_staff:
            return Response({'error': 'You do not have permission to edit this post'}, 
                            status=status.HTTP_403_FORBIDDEN)
            
        serializer = PostSerializer(instance=post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def post_delete_api(request, slug):
    try:
        post = Post.objects.get(slug=slug)
        
        # Check if user is author or staff
        if request.user != post.author and not request.user.is_staff:
            return Response({'error': 'You do not have permission to delete this post'}, 
                            status=status.HTTP_403_FORBIDDEN)
            
        post.delete()
        return Response({'message': 'Post deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

