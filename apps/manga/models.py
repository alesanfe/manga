from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.db import models

# Import centralized logger configuration
from utils.logger_config import logger


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        logger.debug(f"Saving author: {self.name}")
        super().save(*args, **kwargs)
        logger.info(f"Author saved: {self.name}")


class Genre(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        logger.debug(f"Saving genre: {self.name}")
        super().save(*args, **kwargs)
        logger.info(f"Genre saved: {self.name}")

    class Meta:
        ordering = ['name']


class Manga(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'En curso'),
        ('completed', 'Completado'),
        ('hiatus', 'Pausado'),
        ('cancelled', 'Cancelado'),
        ('unknown', 'Desconocido'),
    ]
    
    title = models.CharField(max_length=100, verbose_name='Title')
    alternative_titles = models.TextField(verbose_name='Alternative Titles', blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Author')
    release_year = models.PositiveIntegerField(verbose_name='Release Year', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown', verbose_name='Status')
    image_link = models.URLField(validators=[URLValidator()], verbose_name='Image Link')
    details_link = models.URLField(validators=[URLValidator()], verbose_name='Details Link')
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    genres = models.ManyToManyField(Genre, verbose_name='Genres')
    num_caps = models.IntegerField(verbose_name='Number of Chapters')
    views = models.PositiveIntegerField(verbose_name='Views')
    likes = models.PositiveIntegerField(verbose_name='Likes', default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        logger.debug(f"Saving manga: {self.title}")
        super().save(*args, **kwargs)
        logger.info(f"Manga saved: {self.title} by {self.author.name}")


class Score(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, verbose_name='Manga')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    score = models.FloatField(verbose_name='Score')

    def __str__(self):
        return str(self.score)

    def save(self, *args, **kwargs):
        logger.debug(f"Saving score: {self.score} for {self.manga.title} by {self.user.username}")
        super().save(*args, **kwargs)
        logger.info(f"Score saved: {self.score}/5 for {self.manga.title}")

    class Meta:
        unique_together = ['manga', 'user']
        ordering = ['manga']





