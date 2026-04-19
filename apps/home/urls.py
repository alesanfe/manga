# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Manga Project
"""

from django.urls import path, re_path

from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    # Matches any html file except authentication routes
    re_path(r'^(?!edit|login|register|logout).*\.*', views.pages, name='pages'),

]
