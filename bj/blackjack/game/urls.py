from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.start_game, name='start_game'),
    path('play/', views.play_game, name='play_game'),
    path('hit/', views.hit, name='hit'),
    path('stand/', views.stand, name='stand'),
    path('reset/', views.reset_chips, name='reset_chips'),
]
