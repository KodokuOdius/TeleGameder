from django.shortcuts import redirect, render
from django.http import HttpResponse, Http404
from django.views.generic import ListView

from django.db.models import Q
from .utils import DataMixin
from .models import Users, Games

class BotHome(DataMixin, ListView):
    model = Users
    template_name = "bot/index.html"
    context_object_name = "users"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        games = self.get_games_context()
        context["title"] = "HomePage"

        return context | games


    def get_queryset(self):
        return Users.objects.filter(is_search=True)


def view_gamers(requests, game):
    games = Games.objects.all()
    users = Users.objects.filter(game=game, is_search=True)

    if game not in [game.title for game in games] or list(users) == []:
        # Not Found 404
        return redirect("/")

    context = {
        "title": game,
        "users": users,
        "games": games
    }

    return render(requests, template_name="bot/index.html", context=context)
    



