from django.contrib import admin
from .models import Post, PostImage, Tag

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 3
    fields = ('image',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'tag_list')
    list_filter = ('pub_date', 'author', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PostImageInline]
    date_hierarchy = 'pub_date'

    def tag_list(self, obj):
        return ", ".join([t.name for t in obj.tags.all()])
    tag_list.short_description = 'Etiquetas'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}