# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Manga Project
"""
from django.contrib.auth import authenticate, login
# Create your views here.
from django.shortcuts import render, redirect
from django.views import View

# Import centralized logger configuration
from utils.logger_config import logger
from .forms import LoginForm, SignUpForm, CustomUserEditionForm
from .models import UserProfile


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

class EditUserView(View):
    def get(self, request):
        user = request.user
        if user is not None:
            # Get or create UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            logger.info(f"User: {user.username}, Profile created: {created}")
            logger.info(f"Profile picture: {profile.profile_picture}")
            logger.info(f"Profile picture name: {profile.profile_picture.name if profile.profile_picture else None}")
            
            # Pre-fill form with User data
            form = CustomUserEditionForm(instance=user)
            
            # Pre-fill profile fields
            if profile.profile_picture:
                form.fields['profile_picture'].initial = profile.profile_picture
            if profile.bio:
                form.fields['bio'].initial = profile.bio
            if profile.location:
                form.fields['location'].initial = profile.location
            if profile.website:
                form.fields['website'].initial = profile.website
            if profile.birth_date:
                form.fields['birth_date'].initial = profile.birth_date
            
            return render(request, 'home/user.html', {'form': form, 'user': user, 'profile': profile})
        form = LoginForm(request.POST)
        return render(request, 'accounts/login.html', {'form': form, 'user': user, 'msg': 'Usuario no encontrado', 'success': False})



    def post(self, request):
        user = request.user
        form = CustomUserEditionForm(request.POST, request.FILES, instance=user)
        
        if form.is_valid():
            # Save User fields
            user = form.save()
            
            # Get or create UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Update UserProfile fields
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
            if 'bio' in form.cleaned_data:
                profile.bio = form.cleaned_data['bio']
            if 'location' in form.cleaned_data:
                profile.location = form.cleaned_data['location']
            if 'website' in form.cleaned_data:
                profile.website = form.cleaned_data['website']
            if 'birth_date' in form.cleaned_data:
                profile.birth_date = form.cleaned_data['birth_date']
            
            profile.save()
            logger.info(f"User {user.username} updated successfully")
            return redirect("/")
        
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return render(request, 'home/user.html', {'form': form, 'user': user, 'profile': profile, 'msg': 'Usuario no editado', 'success': False})
