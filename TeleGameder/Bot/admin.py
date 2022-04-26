from django.contrib import admin
from .models import Users, Games
from .forms import UsersForm, GamesForm


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'tg_id', 'username', 'about', 'is_search')
    form = UsersForm



@admin.register(Games)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    form = GamesForm
