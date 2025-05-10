from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from ckeditor.widgets import CKEditorWidget
from .models import Post, Comment, Category, Tag, UserProfile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'website', 'twitter', 'github', 'linkedin']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.TextInput(attrs={'class': 'form-control'}),
            'github': forms.TextInput(attrs={'class': 'form-control'}),
            'linkedin': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    tags_input = forms.CharField(required=False, help_text='Separate tags with commas')
    
    class Meta:
        model = Post
        fields = ['title', 'excerpt', 'content', 'featured_image', 'category', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter post title'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter a short description'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # If editing an existing post, populate the tags field
            self.fields['tags_input'].initial = ', '.join([tag.name for tag in self.instance.tags.all()])
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Handle tags
            if self.cleaned_data.get('tags_input'):
                tags = [tag.strip() for tag in self.cleaned_data['tags_input'].split(',') if tag.strip()]
                instance.tags.clear()
                for tag_name in tags:
                    tag, created = Tag.objects.get_or_create(name=tag_name, defaults={'slug': tag_name.lower().replace(' ', '-')})
                    instance.tags.add(tag)
            self.save_m2m()
        return instance


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your comment here...'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Search posts...'}))

