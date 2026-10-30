from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def login(response):
    return HttpResponse("Hier entsteht bald der Login.")

def dashboard(request):
    return HttpResponse("Hier ist das Dashboard.")