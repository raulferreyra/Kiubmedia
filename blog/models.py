from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag_detail', args=[self.slug])


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_posts',
        verbose_name="Autor"
    )
    content = models.TextField(verbose_name="Contenido")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Etiquetas")
    youtube_url = models.URLField(max_length=200, blank=True, null=True, verbose_name="Link de YouTube (opcional)")
    pub_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de publicación")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_youtube_embed(self):
        if not self.youtube_url:
            return ""
        video_id = ""
        if "v=" in self.youtube_url:
            video_id = self.youtube_url.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in self.youtube_url:
            video_id = self.youtube_url.split("youtu.be/")[-1].split("?")[0]
        if video_id:
            return f'<iframe width="100%" height="450" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
        return ""

    def get_absolute_url(self):
        return reverse('post_detail', args=[self.slug])

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/%Y/%m/%d/')
    
    def __str__(self):
        return f"Imagen en {self.post.title}"