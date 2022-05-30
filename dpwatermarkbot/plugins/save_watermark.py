from asyncio import sleep
from time import time

from pyrogram import filters
from pyrogram.types import Message

from dpwatermarkbot.bot_class import DPWaterMarkBot
from dpwatermarkbot.db import MainDB
from dpwatermarkbot.utils.display_progress import progress_for_pyrogram
from dpwatermarkbot.utils.joinCheck import joinCheck
from dpwatermarkbot.vars import Vars


@DPWaterMarkBot.on_message(
    (filters.document | filters.photo) & filters.private,
    group=3,
)
@joinCheck()
async def add_watermark(c: DPWaterMarkBot, m: Message):
    if m.photo or (m.document and m.document.mime_type.startswith("image/")):
        editable = await m.reply_text("Downloading Image...", quote=True)

        watermark_path = f"{Vars.DOWN_PATH}/{m.from_user.id}/thumb.jpg"

        await sleep(5)
        c_time = time()
        await c.download_media(
            message=m,
            file_name=watermark_path,
            progress=progress_for_pyrogram,
            progress_args=("Downloading watermark...", editable, c_time),
        )
        await editable.delete()
        await m.reply_text(
            (
                "This Saved as Next Video Watermark!\n\n"
                "Now Send any Video to start adding Watermark to the Video!"
            ),
            quote=True,
        )

        await m.stop_propagation()


@DPWaterMarkBot.on_message(
    filters.command(["savethumb", "savewatermark"], Vars.PREFIX_HANDLER)
    & filters.private,
)
@joinCheck()
async def set_watermark(c: DPWaterMarkBot, m: Message):
    db = MainDB(m.from_user.id)
    if m.reply_to_message.photo or (
        m.reply_to_message.document
        and m.reply_to_message.document.mime_type.startswith("image/")
    ):
        save_photo = (
            m.reply_to_message.photo.file_id or m.reply_to_message.document.file_id
        )
        print(save_photo)
        db.set_watermark(str(save_photo))
        await m.reply_text(
            "Saved this photo as your watermark!",
            reply_to_message_id=m.reply_to_message.id,
        )
        caption = f"#SET_WATERMARK\n**UserID:** #id{m.from_user.id}"
        try:
            await c.send_photo(
                Vars.MESSAGE_DUMP,
                save_photo,
                caption=caption,
            )
        except ValueError as ef:
            if "Expected PHOTO, got DOCUMENT file id instead" in str(ef):
                await c.send_document(
                    Vars.MESSAGE_DUMP,
                    save_photo,
                    caption=caption,
                )
    else:
        await m.reply_text("Please reply to a photo to set that as watermark!")
    return


@DPWaterMarkBot.on_message(
    filters.command(["mythumb", "watermark"], Vars.PREFIX_HANDLER) & filters.private,
)
@joinCheck()
async def get_watermark(_, m: Message):
    db = MainDB(m.from_user.id)
    save_photo = db.get_watermark()
    if save_photo is None:
        await m.reply_text("You haven't set any watermark yet!", quote=True)
        return
    try:
        await m.reply_photo(
            save_photo,
            caption="Here is the watermark you have saved!",
            quote=True,
        )
    except ValueError as ef:
        if "Expected PHOTO, got DOCUMENT file id instead" in str(ef):
            await m.reply_document(
                save_photo,
                caption="Here is the watermark you have saved!",
                quote=True,
            )
    return


@DPWaterMarkBot.on_message(
    filters.command(["delthumb", "delwatermark"], Vars.PREFIX_HANDLER)
    & filters.private,
)
@joinCheck()
async def del_watermark(c: DPWaterMarkBot, m: Message):
    db = MainDB(m.from_user.id)
    db.set_watermark(None)
    await m.reply_text("Deleted your saved watermark!", quote=True)
    await c.send_message(
        chat_id=Vars.MESSAGE_DUMP,
        text=f"#DEL_WATERMARK\n**UserID:** #id{m.from_user.id}",
    )
    return
