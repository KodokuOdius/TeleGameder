from django.core.management.base import BaseCommand
from django.conf import settings

from Bot.models import Users, Games

from aiogram import Bot, Dispatcher, executor, types


from asgiref.sync import sync_to_async, async_to_sync

bot = Bot(token=settings.TOKEN)
dp = Dispatcher(bot=bot)



@sync_to_async(thread_sensitive=True)
def create(id, username):
    try:
        return Users.objects.create(
                tg_id=id,
                username=username,
                game=Games.objects.get(pk=2),
                about="None",
                search_game=Games.objects.get(pk=2)
            ), False
    except Exception as ex:
        print(ex)
        return None, True



@dp.message_handler()
async def echo(event: types.Message):

    user, is_exist = await create(
        event.from_user.id,
        event.from_user.username
    )
    
    print(is_exist)


    if not is_exist:
        await event.answer(event.text)

    else:
        await event.answer(f"Welcome\n {event.text}")


class Command(BaseCommand):
    help = "Telegram Bot"

    def handle(self, *args, **options):
        
        # bot = telepot.Bot(token=settings.TOKEN)
        # print(bot.getMe())

        executor.start_polling(dp, skip_updates=True)




