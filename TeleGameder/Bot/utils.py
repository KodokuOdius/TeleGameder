from .models import *

class DataMixin:
    def get_games_context(self, **kwargs):
        context = kwargs
        games = Games.objects.all()
        context["games"] = games

        return context
