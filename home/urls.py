from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='Wethics'),
    path('forecast/',views.forecast,name='Forecast'),
    path('today/',views.today,name='Today')
]

handler404 = "home.views.ren404"
