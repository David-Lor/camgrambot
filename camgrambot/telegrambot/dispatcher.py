import aiogram.types

from ..cameras import CamerasService

dispatcher = aiogram.Dispatcher()


@dispatcher.message()
async def message_handler(message: aiogram.types.Message):
    message_chunks = message.text.strip().split()
    if not message_chunks:
        return

    message_cmd = message_chunks[0]
    if message_cmd == "/start":
        await message.answer("Hello there!")
        return

    if message_cmd == "/cameras":
        await cameras_message_handler(message)
        return


async def cameras_message_handler(message: aiogram.types.Message):
    cameras = CamerasService.cameras

    reply_markup = aiogram.types.InlineKeyboardMarkup(inline_keyboard=[
        [aiogram.types.InlineKeyboardButton(
            text=f"{camera.name} (#{camera.id})",
            callback_data=f"GetCamera_{camera.id}",
        )]
        for camera in cameras
    ])

    await message.bot.send_message(
        chat_id=message.chat.id,
        text=f"{len(cameras)} cameras found:",
        reply_markup=reply_markup,
    )
