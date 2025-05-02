from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, UserSettings, DashboardStats, Task
from .forms import UserProfileForm, UserSettingsForm, TaskForm

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'auth-login-basic.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'auth-login-basic.html')
    return render(request, 'auth-login-basic.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Validate form data
        if not username or not email or not password:
            messages.error(request, 'All fields are required')
            return render(request, 'auth-register-basic.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'auth-register-basic.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'auth-register-basic.html')
        
        # Create the user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'auth-register-basic.html')
            
    return render(request, 'auth-register-basic.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            # In a real application, you would send a password reset email here
            messages.success(request, 'Password reset link sent to your email')
            return redirect('login')
        else:
            messages.error(request, 'Email not found')
    return render(request, 'auth-forgot-password-basic.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    # Sample dashboard stats
    stats = [
        {'title': 'Sales', 'value': 478, 'icon': 'bx-cart', 'color': 'primary'},
        {'title': 'Customers', 'value': 4385, 'icon': 'bx-user', 'color': 'info'},
        {'title': 'Products', 'value': 1324, 'icon': 'bx-package', 'color': 'success'},
        {'title': 'Revenue', 'value': '$12,628', 'icon': 'bx-dollar', 'color': 'warning'}
    ]
    
    # Get user tasks
    tasks = Task.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'tasks': tasks,
        'user': request.user
    }
    return render(request, 'index.html', context)

@login_required
def account_settings(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('account_settings')
    else:
        profile_form = UserProfileForm(instance=request.user.profile)
    
    context = {
        'profile_form': profile_form,
        'user': request.user
    }
    return render(request, 'pages-account-settings-account.html', context)

@login_required
def notification_settings(request):
    if request.method == 'POST':
        settings_form = UserSettingsForm(request.POST, instance=request.user.settings)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, 'Notification settings updated successfully')
            return redirect('notification_settings')
    else:
        settings_form = UserSettingsForm(instance=request.user.settings)
    
    context = {
        'settings_form': settings_form,
        'user': request.user
    }
    return render(request, 'pages-account-settings-notifications.html', context)

@login_required
def tasks_view(request):
    tasks = Task.objects.filter(created_by=request.user).order_by('-created_at')
    context = {
        'tasks': tasks,
        'user': request.user
    }
    return render(request, 'tasks.html', context)

@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, 'Task created successfully')
            return redirect('tasks')
    else:
        form = TaskForm()
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'create-task.html', context)

@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, created_by=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully')
            return redirect('tasks')
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'user': request.user
    }
    return render(request, 'update-task.html', context)

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, created_by=request.user)
    task.delete()
    messages.success(request, 'Task deleted successfully')
    return redirect('tasks')