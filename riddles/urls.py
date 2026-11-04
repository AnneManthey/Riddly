from django.urls import path
from . import views


urlpatterns = [
    path('', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path ('<slug:slug>', views.riddle, name="riddle" )
]