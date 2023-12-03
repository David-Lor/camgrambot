import aiogram

from .dispatcher import dispatcher
from ..settings import Settings


class TelegramBot:
    bot: aiogram.Bot = None

    @classmethod
    async def run(cls):
        cls.bot = aiogram.Bot(
            token=Settings.get().telegrambot.token.get_secret_value(),
        )

        print("Start running bot!")
        await dispatcher.start_polling(cls.bot)
