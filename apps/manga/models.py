from django.db import models
from django.core.validators import URLValidator
from django.contrib.auth.models import User


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name')

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Manga(models.Model):
    title = models.CharField(max_length=100, verbose_name='Title')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Author')
    release_year = models.PositiveIntegerField(verbose_name='Release Year', null=True, blank=True)
    image_link = models.URLField(validators=[URLValidator()], verbose_name='Image Link')
    details_link = models.URLField(validators=[URLValidator()], verbose_name='Details Link')
    genres = models.ManyToManyField(Genre, verbose_name='Genres')
    num_caps = models.IntegerField(verbose_name='Number of Chapters')
    views = models.PositiveIntegerField(verbose_name='Views')

    def __str__(self):
        return self.title


class Score(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, verbose_name='Manga')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    score = models.FloatField(verbose_name='Score')

    def __str__(self):
        return str(self.score)  # Asegúrate de convertir el puntaje a cadena antes de devolverlo

    class Meta:
        unique_together = ['manga', 'user']
        ordering = ['manga']





