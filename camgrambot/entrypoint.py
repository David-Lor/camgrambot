import asyncio

from .telegrambot.bot import TelegramBot
from .cameras import CamerasService


async def amain():
    await CamerasService.load_cameras_to_cache()
    await TelegramBot.run()


def main():
    asyncio.get_event_loop().run_until_complete(amain())
