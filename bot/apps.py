import asyncio
import threading

from django.apps import AppConfig
from bot.handlers import dp, bot_s


class BotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bot"

    def ready(self):
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            loop.run_until_complete(dp.start_polling(bot_s))

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
