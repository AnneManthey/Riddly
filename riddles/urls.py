from django.urls import path
from . import views


urlpatterns = [
    path('', views.login, name="login"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path ('<slug:slug>', views.riddle, name="riddle" )
]