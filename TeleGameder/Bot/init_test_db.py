# from models import Users, Games
import random as r
import sqlite3


username = [
    "Mae Anderson",
    "Mary Kelly",
    "John Sutton",
    "Carolyn Allen",
    "Dustin May",
    "Margaret Green",
    "John Moore",
    "Larry Clark",
    "David Oliver",
    "Lydia Foster"
]

games = [
    "Snake", "PackMan", "Genshin Impact",
    "DOTA 2", "CS:GO", "Elden Rind", "The Walking Dead",
    "Silent Hills"
]


with sqlite3.connect("C:\\Users\\nikol\\OneDrive\\DeskTop\\GitHubTrash\\TeleGameder\\TeleGameder\\db.sqlite3") as db:
    cur = db.cursor()

    def create_user(**data):
        try:
            # Users.objects.create(**data)

            cur.execute(
                """
                INSERT INTO Bot_users
                (tg_id, username, about, is_search, search_game, game)
                VALUES
                ({tg_id}, '{username}', '{about}', {is_search}, '{search_game}', '{game}')
                """.format(
                    **data
                )
            )

            return True
        except Exception as ex:
            print(ex)
            return False
    

    for game in games:
        try:
            cur.execute(
                f"""
                INSERT INTO Bot_games
                (title)
                VALUES ('{game}')
                """
            )
        except Exception as ex:
            print(ex)

        # Games.objects.get_or_create(
        #     title=game
        # )


    for i in range(50):
        data = {
            "tg_id": r.randint(100, 90000),
            "username": r.choice(username),
            "about": "This is TestUser, qwerty!",
            "is_search": r.choice([True, False]),
            "search_game": r.choice(games),
            "game": r.choice(games)
        }
        result = create_user(**data)

        if not result:
            create_user(**data)
