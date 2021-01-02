from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='Home'),
    path('forecast/',views.forecast,name='Forecast'),
    path('today/',views.today,name='Today')
]

