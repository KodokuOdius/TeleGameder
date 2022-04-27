from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async, async_to_sync
from django.conf import settings

from Bot.models import Users, Games

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram import exceptions as Aex

from random import choice as ch

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


# Состояния для регистрации
class RegUser(StatesGroup):
    username = State()
    about = State()
    game = State()
    search = State()
    is_correct = State()


bot = Bot(token=settings.TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())


MainKey = (
    ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    .row(
        KeyboardButton("🤝"),
        KeyboardButton("➡")
    )
)



async def gen_keybord(data: list, inline: bool = False):
    if not inline:
        KeyBoard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        for i, datum in enumerate(data):
            Key = KeyboardButton(datum)
            KeyBoard.add(Key)
            
            # if i % 3:
            #     KeyBoard.row()

    else:
        # callback_data
        KeyBoard = InlineKeyboardMarkup(row_width=1)

        for i, datum in enumerate(data):
            Key = InlineKeyboardButton(datum)
            KeyBoard.add(Key)


    return KeyBoard




@sync_to_async(thread_sensitive=True)
def get_user(id):
    try:
        temp = Users.objects.get(tg_id=id)
        return temp if temp else False

    except Exception as ex:
        print(ex)
        # return None, True

@sync_to_async(thread_sensitive=True)
def get_games():
    try:

        Qset = Games.objects.all()
        temp = [temp.title for temp in Qset]
        return temp
    except Exception as ex:
        print(ex)


@sync_to_async(thread_sensitive=True)
def create_user(data):
    try:
        Users.objects.get_or_create(
            username=data["username"],
            game=data["game"],
            about=data["about"],
            search_game=data["search"],
            tg_id=data["tg"]
        )

        return True
    except Exception as ex:
        print(ex)
        return False



@sync_to_async(thread_sensitive=True)
def get_users_by_prefer(id, game):
    try:
        from django.db.models import Q

        friends = Users.objects.filter(Q(search_game=game) & Q(is_search=1)).exclude(tg_id=id)
        friends = [friend for friend in friends]
        return friends
    except Exception as ex:
        print(ex)


@sync_to_async(thread_sensitive=True)
def update_user(id, *args, **kwargs):
    try:
        user = Users.objects.filter(tg_id=id).update(**kwargs)
        return True
    except Exception as ex:
        print(ex)


@dp.message_handler(state=RegUser.username)
async def username(event: types.Message, state: FSMContext):
    await state.update_data(username=event.text, tg=event.from_user.id)

    await event.answer(
        "Отлично!\n" +
        "Теперь расскажи немного о себе\n" +
        "Можешь написать дополнительную информацию о себе, чтобы найти ту самую команду 'Мечты'"
    )

    await RegUser.about.set()


@dp.message_handler(state=RegUser.about)
async def second(event: types.Message, state: FSMContext):
    from random import shuffle as sh

    await state.update_data(about=event.text)
    temp_data = await get_games()
    sh(temp_data)

    game_key = await gen_keybord(
        data=temp_data[:4]
    )

    await event.answer(
        "Теперь напиши свою любимую игру (оригинально название игры на английском)\n" +
        "Или выбери из списка",
        reply_markup=game_key
    )

    await RegUser.game.set()


@dp.message_handler(state=RegUser.game)
async def game(event: types.Message, state: FSMContext):
    await state.update_data(game=event.text)
    data = await state.get_data()
    game = data["game"]

    small_key = await gen_keybord([game])

    await event.answer(
        "Прекрасно! Я тоже часто играю в эту игру)\n" +
        "Последний вопрос!\n" +
        "В какой игре ты будешь искать друзей?\n" +
        "Можешь написать другую игру (оригинально название игры на английском)" +
        "или нажать на кнопку, чтобы не повторяться",
        reply_markup=small_key
    )


    await RegUser.search.set()



@dp.message_handler(state=RegUser.search)
async def last_question(event: types.Message, state: FSMContext):
    await state.update_data(search=event.text)

    data = await state.get_data()

    await event.answer(
        "Отлично! Вот твоя анкета\n" +
        f"Твой username: {data['username']}\n"
        f"Любимая игра: {data['game']}\n" +
        f"Игра для поиска: {data['search']}\n" +
        f"О себе: \n  {data['about']}",
        # reply_markup=ReplyKeyboardRemove()
    )


    end_key = await gen_keybord(["Да 😁", "Нет заново) 🤣"])
    await event.answer(
        "Всё верно?",
        reply_markup=end_key
    )

    # finish states
    await RegUser.is_correct.set()



@dp.message_handler(state=RegUser.is_correct)
async def finish(event: types.Message, state: FSMContext):
    if event.text == "Да 😁":
        user = await get_user(event.from_user.id)
        data = await state.get_data()
        if not user:
            result = await create_user(data)
        else:
            result = await update_user(
                event.from_user.id,
                username=data["username"],
                game=data["game"],
                about=data["about"],
                search_game=data["search"]
            )

            await state.reset_state()
            return await profile_menu(event)

        # if result:
        #     await event.answer(
        #         "Прекрасно! Я тебя зарегестировал!"
        #     )
        
        # await start_search(event=event, state=state)


    elif event.text == "Нет заново) 🤣":
        await event.answer(
            "Ладно... Заново"
        )
        await event.answer(
            "Напиши свой никнейм (из Steam или какой часто искользуешь в играх)"
        )

        await RegUser.username.set()






class ProfileMenu(StatesGroup):
    menu = State()
    new_search = State()


class SearchState(StatesGroup):
    search = State()


@dp.message_handler(state=ProfileMenu.menu, text="😙")
async def start_search(event: types.Message, state: FSMContext):
    await event.answer(
        "Начнём поиск Тимейтов\n" +
        "➡ - Следующая карточка\n" +
        "🤝 - Отправляет приглашение к дружбе создателю карточки\n\n" +
        "Чтобы закончить с поисками пришли любое сообщение (отличное от содержания кнопок)"
    )
    user = await get_user(event.from_user.id)

    friends = await get_users_by_prefer(event.from_user.id, user.search_game)

    if not friends:
        return await event.answer(
            "Нет пользователей с такой игрой, попробуй выбрать что-то другое\n" +
            "/profile"
        )
    friend = friends.pop()

    await event.answer(
        f"{friend.username}\n" +
        f"Любимая игра: {friend.game}\n" +
        f"Информация: {friend.about}",
        reply_markup=MainKey
    )

    await SearchState.search.set()
    await state.update_data(friend_id=friend.tg_id, friends=friends)


@dp.message_handler(state=SearchState.search)
async def answer(event: types.Message, state: FSMContext):
    answer = event.text
    if answer not in ["🤝", "➡"]:
        await event.answer("Закончим с поиском)")
        await state.reset_state()
        return await profile_menu(event)

    if answer == "🤝":
        data = await state.get_data()
        friend_id = data["friend_id"]

        try:
            user_name = event.from_user.username

            await event.bot.send_message(
                chat_id=friend_id,
                text=(
                    f"Внимание! Твоя корточка понравилась пользователю @{user_name}"
                )
            )

            await event.answer(
                "Твой лайк отправлем этому пользователю\n" +
                "Давай дальше"
            )
            
        except Aex.BotBlocked:
            await event.answer("Этот пользователь заблокировал бота")
        except Exception as ex:
            print(ex)
            await event.answer(
                "Не могу достать твой username из Telegram\n" +
                "Придумай себе username или измени что-то в настройках, тогда я смогу отправить привет!"
            )

    data = await state.get_data()
    friends = data["friends"]

    if not friends:
        await state.reset_state()

        return await event.answer(
            "Закончились пользователи по данной игре (("
        )

    friend = friends.pop()

    await event.answer(
        f"{friend.username}\n" +
        f"Любимая игра: {friend.game}\n" +
        f"Информация:\n {friend.about}",
        reply_markup=MainKey
    )

    await state.update_data(friend_id=friend.tg_id, friends=friends)


@dp.message_handler(state=ProfileMenu.menu, text="😁")
async def new_search_game(event: types.Message):
    from random import shuffle as sh

    temp_data = await get_games()
    sh(temp_data)

    game_key = await gen_keybord(
        data=temp_data[:4]
    )

    await event.answer(
        "Напиши другую игру (оригинально название игры на английском) для поиска\n" +
        "Или выбери из списка",
        reply_markup=game_key
    )
    
    await ProfileMenu.new_search.set()

@dp.message_handler(state=ProfileMenu.new_search)
async def catch_new_game(event: types.Message, state: FSMContext):
    new_search = event.text
    await update_user(
        event.from_user.id,
        search_game=new_search
    )

    await state.reset_state()
    await profile_menu(event)


@dp.message_handler(state=ProfileMenu.menu, text="😑")
async def new_profile(event: types.Message):
    await event.answer(
        "Напиши свой никнейм (из Steam или какой часто искользуешь в играх)"
    )

    await RegUser.username.set()

@dp.message_handler(state=ProfileMenu.menu, text="😣")
async def change_search(event: types.Message, state: FSMContext):
    user = await get_user(event.from_user.id)

    await update_user(
        event.from_user.id,
        is_search=0 if bool(user.is_search) else 1
    )

    await state.reset_state()
    await profile_menu(event)



@dp.message_handler(Command("profile"))
async def profile_menu(event: types.Message):
    user = await get_user(
        id=event.from_user.id
    )

    if not user:
        await start_bot(event)
    else:
        profile_key = (
            ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            .row(
                KeyboardButton("😙"),
                KeyboardButton("😁"),
                KeyboardButton("😣"),
                KeyboardButton("😑")
            )
        )


        await event.answer(
            "Вот твоя анкета\n" +
            f"Твой username: {user}\n" + 
            ("-В активном поиске\n" if bool(user.is_search) else "-Вне поиска\n") +
            f"Любимая игра: {user.game}\n" +
            f"Игра для поиска: {user.search_game}\n" +
            f"О себе: \n  {user.about}",
            reply_markup=profile_key
        )

        await event.answer(
            "😙 - Поиск\n" + 
            "😁 - Изменить игру для поиска\n" +
            "😣 - Изменить поиск\n (Если в поиске, то выйдешь из поиска, и наоборот)\n" +
            "😑 - Написать анкету заново"
        )
        
        await ProfileMenu.menu.set()
        


@dp.message_handler(Command("help"))
async def help(event: types.Message):
    await event.answer(
        "Держись, я верю в тебя!"
    )


@dp.message_handler(Command("start"))
async def start_bot(event: types.Message):

    is_created = await get_user(
        event.from_user.id,
    )

    if is_created:
        # start Search
        await event.answer(event.text)
    else:
        await event.answer(
            "Привет, Я вижу тебя впервые)\n " +
            "Здесь ты смодешь познакомиться с тимейтов по разным играм и найти друзей\n " +
            "Тебе нужно всего-то нужно ответь на несколько вопросов\n " +
            "Начнём!"
        )

        await event.answer(
            "Напиши свой никнейм (из Steam или какой часто искользуешь в играх)"
        )

        await RegUser.username.set()
        

    

async def start(dp: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("profile", "Профиль")
    ])

    
async def shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()


# Start bot with Django
class Command(BaseCommand):
    help = "Telegram Bot"

    def handle(self, *args, **options):

        print(args)
        print(options)
        
        # bot = telepot.Bot(token=settings.TOKEN)
        # print(bot.getMe())

        executor.start_polling(
            dp, 
            #skip_updates=True,
            on_startup=start,
            on_shutdown=shutdown
        )




