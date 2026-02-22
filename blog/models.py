from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
import re


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
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
    )

    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_posts',
        verbose_name="Autor"
    )
    lead = models.TextField(blank=True, verbose_name="Gorro / Introducción")
    excerpt = models.TextField(
        max_length=300,
        blank=True,
        verbose_name="Resumen (excerpt) para SEO y meta description",
        help_text="Máximo 300 caracteres. Se usa en meta tags y como descripción en buscadores."
    )
    content = models.TextField(verbose_name="Contenido principal")
    closing = models.TextField(blank=True, verbose_name="Cierre / Conclusión")
    tags = models.ManyToManyField('Tag', blank=True, verbose_name="Etiquetas")
    youtube_url = models.URLField(
        max_length=200, blank=True, null=True, verbose_name="Link de YouTube (opcional)")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Estado"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Destacado"
    )
    reading_time = models.PositiveIntegerField(
        default=0,
        verbose_name="Tiempo de lectura (minutos)",
        editable=False  # se calcula automáticamente
    )
    pub_date = models.DateTimeField(
        default=timezone.now, verbose_name="Fecha de publicación")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Calcular tiempo de lectura aproximado (200 palabras por minuto)
        if self.content:
            word_count = len(re.findall(r'\w+', self.content))
            self.reading_time = max(1, round(word_count / 200))

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

    def get_related_posts(self):
        # Últimos 4 posts con al menos una etiqueta en común, excluyendo el actual
        if not self.tags.exists():
            return Post.objects.none()
        return Post.objects.filter(
            status='published',
            tags__in=self.tags.all()
        ).exclude(id=self.id).distinct().order_by('-pub_date')[:4]

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class PostImage(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/%Y/%m/%d/')

    def __str__(self):
        return f"Imagen en {self.post.title}"
