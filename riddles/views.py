from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Door
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {"form": form})

@login_required(login_url="login")
def dashboard(request):
    doors = Door.objects.filter(user=request.user).order_by('number')
    return render(request, 'dashboard.html', {'doors': doors})

@login_required(login_url="login")
def riddle(request, slug):
    door = get_object_or_404(Door, slug=slug, user=request.user)
    if request.method == "POST" and not door.solved:
        answer = request.POST.get("answer", "").strip().lower()
        door.attempts += 1
        if answer and door.solution.strip().lower() in answer:
            door.solved = True
            door.solved_at = timezone.now()
            door.save()
            messages.success(request, "Yay!.")
            return redirect("dashboard")
        door.save()
        messages.error(request, "Nö. Nächster Versuch!")
        return redirect("riddle", slug=slug)
    return render(request, 'riddle.html', {'door': door})


def logout(request):
    if request.method == "POST":
        auth_logout(request)
    return redirect("login")