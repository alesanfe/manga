# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.contrib.auth.models import User
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views import View

from .forms import LoginForm, SignUpForm, CustomUserEditionForm


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
            form = CustomUserEditionForm(instance=user)
            return render(request, 'home/user.html',{'form': form, 'user': user})
        form = LoginForm(request.POST)
        return render(request, 'accounts/login.html', {'form': form, 'user': user, 'msg': 'Usuario no encontrado', 'success': False})



    def post(self, request):
        user = request.user
        form = CustomUserEditionForm(request.POST, instance=user)
        user = form.instance
        if form.is_valid():
            print("Fufa POST")
            form.save()
            return redirect("/")
        return render(request, 'home/user.html', {'form': form, 'user': user, 'msg': 'Usuario no editado', 'success': False})
