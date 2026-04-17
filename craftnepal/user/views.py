from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import *


# Create your views here.
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "User Created Successfully")
            return redirect("/auth/register")
        else:
            messages.add_message(request, messages.ERROR, "Error Creating User")
            return render(request, "user/register.html", {"form": form})

    context = {"form": UserCreationForm()}

    return render(request, "user/register.html", context)


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request,username=data['username'], password=data['password'])

            if user is not None:
                return redirect("/")
            else:
                messages.add_message(request, messages.ERROR, "Invalid Credentials")
                return render(request, "user/login.html", {"form": form})
    context = {"form": LoginForm}

    return render(request, "user/login.html", context)


def logout_user(request):
    logout(request)
    return redirect("/")
