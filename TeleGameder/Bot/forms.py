from django import forms

from .models import Users, Games

class UsersForm(forms.ModelForm):

    class Meta:
        models = Users
        fields = (
            "tg_id", "username",
            "game", "about",
            "search_game",
            "is_search"
        )
        widgets = {
            "username": forms.TextInput
        }



class GamesForm(forms.ModelForm):

    class Meta:
        models = Games
        fields = ("title",)