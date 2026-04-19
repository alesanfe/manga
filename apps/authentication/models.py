# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Manga Project
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator

# Import centralized logger configuration
from utils.logger_config import logger


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, verbose_name='Profile Picture')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Bio')
    location = models.CharField(max_length=100, blank=True, verbose_name='Location')
    website = models.URLField(blank=True, validators=[URLValidator()], verbose_name='Website')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Birth Date')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        logger.debug(f"Saving profile for user: {self.user.username}")
        super().save(*args, **kwargs)
        logger.info(f"Profile saved for user: {self.user.username}")
