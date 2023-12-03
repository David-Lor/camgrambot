import datetime
import traceback

import aiogram.types

from ..cameras import Camera, CamerasService


INLINE_QUERY_GET_CAMERA = "GetCamera_"
INLINE_QUERY_UPDATE_CAMERA = "UpdateCamera_"

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
    elif query.data.startswith(INLINE_QUERY_UPDATE_CAMERA):
        await update_camera_button_query_handler(query)

    await query.bot.answer_callback_query(query.id)


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
        picture_input_file, reply_markup, caption = await get_camera_message(camera)

        await query.bot.send_photo(
            chat_id=chat_id,
            photo=picture_input_file,
            reply_markup=reply_markup,
            caption=caption,
        )

    except Exception:
        traceback.print_exc()
        await query.bot.send_message(
            chat_id=chat_id,
            text="Error trying to get camera snapshot"
        )


async def update_camera_button_query_handler(query: aiogram.types.CallbackQuery):
    chat_id = query.message.chat.id
    camera_id = query.data.removeprefix(INLINE_QUERY_UPDATE_CAMERA)

    camera = await CamerasService.get_camera_by_id(camera_id)
    if not camera:
        # TODO Show some alert
        return

    # noinspection PyBroadException
    try:
        picture_input_file, reply_markup, caption = await get_camera_message(camera)

        # TODO Detect when the picture is not updated (same as last sent)
        await query.bot.edit_message_media(
            chat_id=chat_id,
            message_id=query.message.message_id,
            media=aiogram.types.InputMediaPhoto(media=picture_input_file, caption=caption),
            reply_markup=reply_markup,
        )

    except Exception:
        traceback.print_exc()
        # TODO Show some alert


async def get_camera_message(camera: Camera) -> tuple[aiogram.types.input_file.BufferedInputFile, aiogram.types.InlineKeyboardMarkup, str]:
    picture_bytes, picture_timestamp = await CamerasService.get_camera_picture(camera.id)
    picture_datetime = datetime.datetime.fromtimestamp(picture_timestamp, tz=datetime.timezone.utc).astimezone()
    picture_datetime_text = picture_datetime.strftime("%d/%m/%y %H:%M:%S")
    picture_input_file = aiogram.types.input_file.BufferedInputFile(
        file=picture_bytes,
        filename=f"Camera_{camera.id}_{picture_timestamp}.jpg",
    )

    reply_markup = aiogram.types.InlineKeyboardMarkup(inline_keyboard=[
        [aiogram.types.InlineKeyboardButton(
            text="Update",
            callback_data=INLINE_QUERY_UPDATE_CAMERA + camera.id,
        )]
    ])

    caption = f"Camera {camera.name} (#{camera.id})\n{picture_datetime_text}"

    return picture_input_file, reply_markup, caption
