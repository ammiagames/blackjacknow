from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.start_hand, name='start_hand'),
    path('play/', views.play_hand_view, name='play_hand'),
    path('hit/', views.hit_view, name='hit'),
    path('stand/', views.stand_view, name='stand'),
    path('reset/', views.reset_chips_view, name='reset_chips'),
    path('insurance/', views.insurance_view, name='insurance'),
    path('even_money/', views.even_money_view, name='even_money'),
    path('double/', views.double_view, name='double'),
    path('split/', views.split_view, name='split'),
]
