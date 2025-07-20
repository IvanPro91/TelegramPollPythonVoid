import traceback
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from config.settings import TELEGRAM_BOT_TOKEN

bot_s = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_welcome_command(message: Message) -> None:
    await bot_s.send_message(
        message.from_user.id,
        f"Используйте команду '/send_quest_module' для отображения викторины",
    )


@dp.message(Command("send_quest_module"))
async def send_quest_module(message: Message) -> None:
    from polling.models import PrivatePoll
    from bot.models import TelegramUser

    user = await chk_and_get_user(message)

    anonymous = message.message_thread_id == 9876 or message.chat.type == "supergroup"
    await send_poll(
        cls_telegram_user=TelegramUser,
        cls_private_poll=PrivatePoll,
        message_chat_id=message.chat.id,
        message_thread_id=message.message_thread_id,
        anonymous=anonymous,
    )


@dp.message()
async def all_message(message: types.Message):
    user = await chk_and_get_user(message)

    # Выводим информацию
    print(
        f"Дата {datetime.now()}\n"
        f"Номер чата: {message.chat.id}\n"
        f"Название чата: {message.chat.title}\n"
        f"ID пользователя: {message.from_user.id}\n"
        f"Тема: {message.message_thread_id}\n"
        f"Пользователь:  {user}\n"
        f"Количество побед: {user.count_winner}\n"
        f"Получено сообщение: {message.from_user.first_name} {message.from_user.last_name}\n"
        f"{message.text}",
        "\n\n\n",
    )

    # Проверяем, количество побед у пользователя
    if False:
        if user.count_winner == 0:
            await bot_s.delete_message(message.chat.id, message.message_id)
            try:
                await bot_s.send_message(
                    message.from_user.id,
                    f"Пройдите викторину и получите баллы",
                )
                await send_poll(
                    cls_telegram_user=TelegramUser,
                    cls_private_poll=PrivatePoll,
                    message_chat_id=message.from_user.id,
                    message_thread_id=message.message_thread_id,
                    anonymous=anonymous,
                )
                return None
            except Exception as err:
                await bot_s.send_message(
                    message.chat.id,
                    f"Вы не можете писать в группу, пока у вас {user.count_winner} баллов по викторине. "
                    f"Используйте команду /send_quest_module лично у бота @quests_and_answers_bot",
                )
                return None


async def chk_and_get_user(message):
    from bot.models import TelegramUser

    # Получаем сущность пользователя
    user: TelegramUser = await TelegramUser.get_or_create_user(
        message_thread_id=message.message_thread_id,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    return user


@dp.callback_query(F.data.startswith("chk_quest_"))
async def cmd_start(call: CallbackQuery):
    from polling.models import PrivatePoll

    qst_id = call.data.replace("chk_quest_", "")
    info_poll = await PrivatePoll.get_private_poll(qst_id)
    msg = (
        f"Исправление викторины от \n{info_poll['user']}\nномер викторины: {info_poll['id_poll']}"
        f"\nНомер викторины пользователя: {qst_id}"
    )

    await bot_s.send_message("293720526", msg)
    await call.answer("Запрос на исправление отправлен!", show_alert=False)


async def send_poll(
    cls_telegram_user,
    cls_private_poll,
    message_thread_id=None,
    message_chat_id=293720526,
    anonymous=True,
    poll_id=None,
):
    from polling.models import Poll

    data = await Poll.do_poll(poll_id)
    try:
        data_poll = await bot_s.send_poll(
            message_chat_id,
            question=f"#{data['id_poll']} {data["question"]}",
            options=data["options"],
            explanation=data["explanation"],
            type="quiz",
            correct_option_id=data["correct_option_id"],
            message_thread_id=message_thread_id,
            is_anonymous=anonymous,
        )
        if not anonymous:
            poll_id = data_poll.poll.id
            user = await cls_telegram_user.get_user_from_chat_id(message_chat_id)
            await cls_private_poll.add_private_poll(
                data["poll"], poll_id, user, correct_option_id=data["correct_option_id"], ball=1
            )
    except Exception as err:
        await bot_s.send_message("293720526", f"Удалить опрос, или отредактировать '{data['id_poll']}'")
        print(traceback.format_exc())


@dp.poll_answer()
async def poll_answer(poll_answer: types.PollAnswer):
    from bot.models import TelegramUser
    from polling.models import PrivatePoll

    answer_ids = poll_answer.option_ids
    user_id = poll_answer.user.id
    id_created_poll = poll_answer.poll_id

    user = await TelegramUser.get_user_from_chat_id(poll_answer.user.id)
    position, count_winner = await PrivatePoll.set_answer_poll(answer_ids, user, id_created_poll)
    if position:
        poll = await PrivatePoll.get_user_private_poll(user, id_created_poll)
        inline_kb_list = [
            [
                InlineKeyboardButton(
                    text="Запрос на исправление",
                    callback_data=f"chk_quest_{id_created_poll}",
                )
            ],
        ]

        status, msg = await user.set_position_winner(position)
        if status:
            chat_id = "-1002302236831"
            message_thread_id = 9876
            raiting_msg = f"Участник {poll['user']}! {msg} по рейтингу, Ваша позиция {position}!"
            print(raiting_msg)
            if position < 3:
                await bot_s.send_message(chat_id, message_thread_id=message_thread_id, text=raiting_msg)

        await bot_s.send_message(
            poll_answer.user.id,
            f"{msg} по рейтингу!\nПозиция: {position}\nКоличество побед: {count_winner}!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_kb_list),
        )

        await send_poll(
            cls_telegram_user=TelegramUser,
            cls_private_poll=PrivatePoll,
            message_chat_id=poll_answer.user.id,
            anonymous=False,
        )
        print(answer_ids, user_id, id_created_poll)
