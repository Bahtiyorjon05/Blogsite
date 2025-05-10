from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Post, Category, Tag, Comment, UserProfile
from .forms import PostForm, CommentForm
from .views import PostCreateView, PostUpdateView, PostDetailView

User = get_user_model()

class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.tag = Tag.objects.create(name='test-tag')
        self.post = Post.objects.create(
            title='Test Post',
            content='Test Content',
            author=self.user,
            category=self.category,
            status='published'
        )
        self.post.tags.add(self.tag)

    def test_post_creation(self):
        self.assertEqual(f'{self.post.title}', 'Test Post')
        self.assertEqual(f'{self.post.author}', 'testuser')
        self.assertEqual(f'{self.post.category}', 'Test Category')
        self.assertEqual(self.post.status, 'published')
        self.assertEqual(self.post.tags.count(), 1)
        self.assertEqual(str(self.post), 'Test Post')

    def test_get_absolute_url(self):
        self.assertEqual(
            self.post.get_absolute_url(),
            reverse('post_detail', kwargs={'slug': self.post.slug})
        )


class PostViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.tag = Tag.objects.create(name='test-tag')
        self.post = Post.objects.create(
            title='Test Post',
            content='Test Content',
            author=self.user,
            category=self.category,
            status='published'
        )
        self.post.tags.add(self.tag)

    def test_post_list_view(self):
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertTemplateUsed(response, 'blog/post_list.html')

    def test_post_detail_view(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertTemplateUsed(response, 'blog/post_detail.html')

    def test_post_create_view_requires_login(self):
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_post_create_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/create_post.html')

    def test_post_update_view_authorized(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('update_post', kwargs={'slug': self.post.slug}),
            {
                'title': 'Updated Title',
                'content': 'Updated content',
                'category': self.category.id,
                'status': 'published'
            }
        )
        self.assertEqual(response.status_code, 302)  # Should redirect after successful update
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')

    def test_post_delete_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_post', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 302)  # Should redirect after deletion
        self.assertEqual(Post.objects.count(), 0)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test Content',
            author=self.user,
            status='published'
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test Comment'
        )

    def test_comment_creation(self):
        self.assertEqual(str(self.comment), "testuser's comment on Test Post")
        self.assertEqual(self.post.comments.count(), 1)
        self.assertEqual(self.post.comments.first().content, 'Test Comment')


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )

    def test_category_creation(self):
        self.assertEqual(str(self.category), 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')


class TagModelTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name='Test Tag')

    def test_tag_creation(self):
        self.assertEqual(str(self.tag), 'Test Tag')
        self.assertEqual(self.tag.slug, 'test-tag')


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='Test Bio',
            website='https://example.com',
            twitter='testuser',
            github='testuser',
            linkedin='testuser'
        )

    def test_profile_creation(self):
        self.assertEqual(str(self.profile), "testuser's Profile")
        self.assertEqual(self.profile.bio, 'Test Bio')
        self.assertEqual(self.profile.website, 'https://example.com')
