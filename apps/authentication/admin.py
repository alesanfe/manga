# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Manga Project
"""

from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'website', 'birth_date')
    list_filter = ('birth_date',)
    search_fields = ('user__username', 'user__email', 'location')
    readonly_fields = ('user',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('profile_picture', 'bio', 'location', 'website', 'birth_date')
        }),
    )
