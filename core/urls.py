# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Manga Project
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import path, include  # add this

# Import centralized logger configuration
from utils.logger_config import logger

urlpatterns = [
    # Simple health endpoint for orchestration checks
    path('health/', lambda request: JsonResponse({'status': 'ok'})),
    path('admin/', admin.site.urls),          # Django admin route
    path("", include("apps.authentication.urls")), # Auth routes - login / register

    # ADD NEW Routes HERE
    path("", include('apps.manga.urls')), # Manga routes - list, detail

    # Leave `Home.Urls` as last the last line
    path("", include("apps.home.urls")),


]

# Serve media files in development - must come before other routes
urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns

logger.info("URL patterns loaded")
