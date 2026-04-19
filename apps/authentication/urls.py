# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Manga Project
"""

from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import login_view, register_user, EditUserView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("edit/", EditUserView.as_view(), name="edit")
]
