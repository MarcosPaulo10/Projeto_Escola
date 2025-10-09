from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_comunicacao, name='home_comunicacao'),
]