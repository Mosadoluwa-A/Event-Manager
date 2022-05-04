from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .forms import ConvenerLogin


def home(request):
    return render(request, 'home.html')

# Auth


def login_user(request):
    if request.method == "POST":
        convener = authenticate(request, email=request.POST['email'], password=request.POST['password'])
        if convener is None:
            return render(request, '404.html')
        login(request, convener)
        messages.success(request, "Login Success")
        return redirect(home)

    form = ConvenerLogin
    return render(request, 'login.html', {"form": form})


def logout_user(request):
    if request.method == "POST":
        logout(request)
        return redirect(login_user)
