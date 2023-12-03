import traceback

import aiogram.types

from ..cameras import CamerasService


INLINE_QUERY_GET_CAMERA = "GetCamera_"

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


@dispatcher.callback_query()
async def callback_query_handler(query: aiogram.types.CallbackQuery):
    if query.data.startswith(INLINE_QUERY_GET_CAMERA):
        await get_camera_button_query_handler(query)
        return


async def cameras_message_handler(message: aiogram.types.Message):
    cameras = CamerasService.cameras

    reply_markup = aiogram.types.InlineKeyboardMarkup(inline_keyboard=[
        [aiogram.types.InlineKeyboardButton(
            text=f"{camera.name} (#{camera.id})",
            callback_data=INLINE_QUERY_GET_CAMERA + camera.id,
        )]
        for camera in cameras.values()
    ])

    await message.bot.send_message(
        chat_id=message.chat.id,
        text=f"{len(cameras)} cameras found:",
        reply_markup=reply_markup,
    )


async def get_camera_button_query_handler(query: aiogram.types.CallbackQuery):
    chat_id = query.message.chat.id
    camera_id = query.data.removeprefix(INLINE_QUERY_GET_CAMERA)

    camera = await CamerasService.get_camera_by_id(camera_id)
    if not camera:
        await query.bot.send_message(
            chat_id=chat_id,
            text=f"Camera #{camera_id} not found!"
        )
        return

    # noinspection PyBroadException
    try:
        picture_bytes, picture_timestamp = await CamerasService.get_camera_picture(camera.id)
        picture_input_file = aiogram.types.input_file.BufferedInputFile(
            file=picture_bytes,
            filename=f"Camera_{camera.id}_{picture_timestamp}.jpg",
        )

        await query.bot.send_photo(
            chat_id=chat_id,
            photo=picture_input_file,
            caption=f"Camera {camera.name} (#{camera.id})",
        )

    except Exception:
        traceback.print_exc()
        await query.bot.send_message(
            chat_id=chat_id,
            text="Error trying to get camera snapshot"
        )
