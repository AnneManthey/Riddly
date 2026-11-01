from django.shortcuts import render
from .models import Door

# Create your views here.

def login(request):
    return render(request, 'login.html')

def dashboard(request):
    doors = Door.objects.all()
    return render(request, 'dashboard.html', {'doors': doors})