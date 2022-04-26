from django.db import models


class Users(models.Model):
    tg_id = models.PositiveIntegerField(
        unique=True,
        verbose_name="Telegram ID"
    )
    username = models.CharField(
        verbose_name="UserName in Bot",
        max_length=255
    )
    game = models.ForeignKey(
        to="Bot.Games",
        to_field="title",
        verbose_name="Favorite Game",
        max_length=255,
        on_delete=models.DO_NOTHING
    )
    about = models.TextField(
        verbose_name="Personal Info"
    )
    search_game = models.CharField(
        verbose_name="Game for search",
        max_length=255
    )
    is_search = models.BooleanField(
        default=True
    )


    def __str__(self) -> str:
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        



class Games(models.Model):
    title = models.CharField(
        unique=True,
        verbose_name="Game Title",
        max_length=255
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Game"
        verbose_name_plural = "Games"
