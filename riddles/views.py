from django.shortcuts import render, redirect
from .models import Door
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout 



def login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {"form": form})


def dashboard(request):
    doors = Door.objects.all().order_by('number')
    return render(request, 'dashboard.html', {'doors': doors})


def riddle(request, slug):
    door = Door.objects.get(slug=slug)
    return render(request, 'riddle.html',{'door': door})


def logout(request):
    if request.method == "POST":
        logout(request)  
        return redirect("login")