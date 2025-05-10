from django.contrib import admin
from .models import Post, Category, Tag, Comment, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'content', 'date_created')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'category', 'status', 'date_created', 'views', 'like_count', 'comment_count')
    list_filter = ('status', 'date_created', 'category')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'date_created'
    filter_horizontal = ('tags', 'likes')
    readonly_fields = ('views', 'date_created', 'date_updated')
    inlines = [CommentInline]
    
    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = 'Likes'
    
    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'post', 'author', 'date_created', 'parent', 'like_count')
    list_filter = ('date_created',)
    search_fields = ('content', 'author__username', 'post__title')
    readonly_fields = ('date_created',)
    
    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = 'Likes'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'website', 'twitter', 'github', 'linkedin')
    search_fields = ('user__username', 'user__email', 'bio')