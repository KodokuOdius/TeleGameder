from django.urls import path, re_path
from . import views


app_name = 'Bot'
urlpatterns = [
    path("", views.BotHome.as_view(), name="home"),
    path("/<str:game>/", views.view_gamers, name="game")
]
