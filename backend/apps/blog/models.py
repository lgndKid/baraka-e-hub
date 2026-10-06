from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Article(models.Model):
    titre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    contenu = models.TextField()
    image = models.ImageField(upload_to="blog/", blank=True, null=True)
    date_publication = models.DateTimeField(default=timezone.now)
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="articles",
    )
    publie = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date_publication"]

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titre)[:200] or "article"
            slug, i = base, 2
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, i = f"{base}-{i}", i + 1
            self.slug = slug
        super().save(*args, **kwargs)
