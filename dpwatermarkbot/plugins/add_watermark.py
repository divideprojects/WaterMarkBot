from asyncio import sleep
from datetime import timedelta
from os import makedirs, path
from time import time
from traceback import format_exc

from humanfriendly import format_timespan
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, Message

from dpwatermarkbot import LOGGER
from dpwatermarkbot.bot_class import DPWaterMarkBot
from dpwatermarkbot.db import LocalDB, MainDB
from dpwatermarkbot.utils.caching import user_cache_check, user_cache_reload
from dpwatermarkbot.utils.clean import delete_all, delete_trash
from dpwatermarkbot.utils.constants import Constants
from dpwatermarkbot.utils.display_progress import human_bytes, progress_for_pyrogram
from dpwatermarkbot.utils.ffmpeg import gen_ss, vidmark
from dpwatermarkbot.utils.ikb import ikb
from dpwatermarkbot.utils.joinCheck import joinCheck
from dpwatermarkbot.utils.upload_utils import streamtape_upload
from dpwatermarkbot.utils.vid_utils import extract_vid_data
from dpwatermarkbot.vars import Vars

l_dict = {}


@DPWaterMarkBot.on_message(
    (filters.document | filters.video) & filters.private,
    group=5,
)
@joinCheck()
async def add_watermark(c: DPWaterMarkBot, m: Message):
    user_id = m.from_user.id
    db = MainDB(user_id)

    cache_status, cache_time = await user_cache_check(m)

    if cache_status:
        await m.reply_text(
            "Spam protection active!\n"
            f"Please try again after {timedelta(seconds=cache_time)} seconds",
        )
        return

    working_dir = f"{Vars.DOWN_PATH}/"
    if not path.exists(working_dir):
        makedirs(working_dir)

    watermark_path = f"{Vars.DOWN_PATH}/{user_id}/thumb.jpg"
    if not path.exists(watermark_path):
        saved_watermark = db.get_watermark()
        # If no custom watermark saved by user and did not even send one!
        if saved_watermark is None:
            await m.reply_text(
                "You Didn't Set Any Watermark!\n\nSend any JPG or PNG Picture ...",
            )
            return
        await c.download_media(saved_watermark, file_name=watermark_path)

    if not (m.video or m.document.mime_type.startswith("video/")):
        await m.reply_text(
            "This is not a Video!\nI need a proper Video to add watermark!",
            quote=True,
        )
        return

    if LocalDB.get("working"):
        await m.reply_text(
            (
                "Sorry, Currently I am busy with another Task!\n\n"
                "Please Try Again After Sometime!"
            ),
        )
        return

    l_dict[f"vid_{user_id}"] = m
    await m.reply_text(
        (
            "<b>Choose Upload Type</b>\n\n"
            "<b>📁 File:</b> <i>Send the Merged Video as a Telegram Document</i>\n"
            "<b>🎥 Video:</b> <i>Send the Merged Video as a Telegram Video</i>\n"
            "<b>🌐 Upload to StreamTape:</b> <i>Upload the Video to online website <a "
            "href='https://streamtape.com/'>StreamTape</a></i> "
        ),
        disable_web_page_preview=True,
        reply_markup=ikb(
            [
                [("📁 File", "upload_type.file"), ("🎥 Video", "upload_type.video")],
                [("🌐 Upload to StreamTape", "upload_type.streamtape")],
                [
                    ("🔙 Back", "back_all_vids"),
                    ("Cancel ❌", f"cancel_add.{user_id}"),
                ],
            ],
        ),
    )


@DPWaterMarkBot.on_callback_query(filters.regex("^upload_type."))
async def main_work(c: DPWaterMarkBot, q: CallbackQuery):
    user_id = q.from_user.id
    qmsg = q.message
    db = MainDB(user_id)

    watermark_path = f"{Vars.DOWN_PATH}/{user_id}/thumb.jpg"
    await qmsg.edit_text("Downloading Video...")
    LocalDB.set("working", True)
    msg = l_dict[f"vid_{user_id}"]
    await user_cache_reload(q)
    upload_type = q.data.split(".")[1]

    LocalDB.set("chat_id", user_id)
    LocalDB.set("message", qmsg.id)

    dl_loc = f"{Vars.DOWN_PATH}/{user_id}/"
    if not path.isdir(dl_loc):
        makedirs(dl_loc)

    the_media, logs_msg = None, None
    user_info = f"<b>UserID:</b> #id{user_id}\n**Name:** {q.from_user.mention}"
    # --- Done --- #

    try:
        forwarded_video = await l_dict[f"vid_{user_id}"].forward(Vars.MESSAGE_DUMP)
        logs_msg = await c.send_message(
            chat_id=Vars.MESSAGE_DUMP,
            text=f"Download Started!\n\n{user_info}",
            reply_to_message_id=forwarded_video.id,
            disable_web_page_preview=True,
            reply_markup=Constants.ban_kb(user_id),
        )
        public_log = await c.send_message(
            chat_id=Vars.PUBLIC_LOGS,
            text=f"Download Started!\n\n**UserID:** `{user_id}`",
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN,
        )
        await sleep(3)
        c_time = time()
        the_media = await c.download_media(
            message=msg,
            file_name=dl_loc,
            progress=progress_for_pyrogram,
            progress_args=("<b>Downloading Video...</b>", qmsg, c_time),
        )
        if the_media is None:
            LOGGER.error("Download Failed!")
            LOGGER.error(format_exc())
            await qmsg.edit_text("Unable to Download The Video!")
            return
    except Exception as ef:
        await delete_trash(the_media)
        LOGGER.error(f"Download Failed: {ef}")
        LOGGER.error(format_exc())
        await qmsg.edit_text("Unable to Download The Video!")
        return

    watermark_position = db.get_position()
    watermark_dict = {
        "5:main_h-overlay_h": "Bottom Left",
        "main_w-overlay_w-5:main_h-overlay_h-5": "Bottom Right",
        "main_w-overlay_w-5:5": "Top Right",
        "5:5": "Top Left",
    }
    position_tag = watermark_dict[watermark_position]

    # Size of watermark
    watermark_size = db.get_size()

    await qmsg.edit_text(
        f"Trying to Add Watermark to the Video at {position_tag} Corner...\n\nPlease Wait!",
    )
    await logs_msg.edit_text(
        f"Trying to Add Watermark to the Video at {position_tag} Corner...\n\nPlease Wait!",
        reply_markup=Constants.ban_kb(user_id),
    )
    await public_log.edit_text(
        f"Trying to Add Watermark to the Video at {position_tag} Corner...\n\nPlease Wait!",
    )

    duration, _, _ = await extract_vid_data(output_vid=the_media)

    the_media_file_name = path.basename(the_media)
    main_file_name = path.splitext(the_media_file_name)[0]
    output_vid = f"{main_file_name}_[{user_id}]_[@{Vars.BOT_USERNAME}].mp4"
    try:
        output_vid = await vidmark(
            the_media,
            qmsg,
            watermark_path,
            output_vid,
            duration,
            logs_msg,
            Vars.PRESET,
            watermark_position,
            watermark_size,
            user_id,
            public_log,
        )
    except Exception as err:
        LOGGER.error(f"Unable to Add Watermark: {err}")
        LOGGER.error(format_exc())
        await qmsg.edit_text("Unable to add Watermark!")
        await logs_msg.edit_text(
            f"#ERROR: Unable to add Watermark!\n\n**Error:** `{err}`",
        )
        await public_log.delete()
        await delete_all()
        return
    if output_vid is None:
        await qmsg.edit_text("Something went wrong!")
        await logs_msg.edit_text("#ERROR: Something went wrong!")
        await public_log.delete()
        await delete_all()
        return

    await qmsg.edit_text("Watermark Added Successfully!\n\nTrying to Upload...")
    await logs_msg.edit_text(
        "Watermark Added Successfully!\n\nTrying to Upload...",
        reply_markup=Constants.ban_kb(user_id),
    )
    await public_log.edit_text("Watermark Added Successfully!\n\nTrying to Upload...")

    duration, width, height = await extract_vid_data(output_vid=output_vid)

    video_thumbnail = await gen_ss(
        user_id=user_id,
        duration=duration,
        output_vid=output_vid,
        width=width,
        height=height,
    )

    # --- Upload --- #
    forward_vid = None
    file_size = path.getsize(output_vid)

    if Vars.STREAMTAPE_DEFAULT or (file_size > 2097152000):
        edit_msg = (
            (
                f"**File Size:** {human_bytes(file_size)}\n"
                "Uploading file to StreamTape...!"
            )
            if Vars.STREAMTAPE_DEFAULT
            else (
                "Sed!\n\n"
                f"File Size Become {human_bytes(file_size)}!!\n"
                "I can't upload files to Telegram with size more  than 2GB!\n\n"
                "So Now Uploading to Streamtape ..."
            )
        )

        await qmsg.edit_text(edit_msg)
        await logs_msg.edit_text(edit_msg, reply_markup=Constants.ban_kb(user_id))
        await public_log.edit_text(edit_msg)
        LocalDB.deldb()
        LocalDB.set("working", False)
        await streamtape_upload(
            qmsg,
            output_vid,
            file_size,
            video_thumbnail,
            logs_msg,
            public_log,
            user_id,
        )
        await delete_all()
        await delete_trash(output_vid)
        return

    await sleep(5)
    LocalDB.deldb()
    LocalDB.set("working", False)
    caption = (
        f"**File Name:** `{output_vid}`\n"
        f"**Video Duration:** `{format_timespan(duration)}`\n"
        f"**File Size:** `{human_bytes(file_size)}`\n\n{Vars.CAPTION}"
    )
    try:
        if upload_type == "video":
            sent_vid = await c.send_video(
                chat_id=qmsg.chat.id,
                video=output_vid,
                caption=caption,
                thumb=video_thumbnail,
                duration=duration,
                width=width,
                height=height,
                supports_streaming=True,
                reply_markup=Constants.support_kb,
                progress=progress_for_pyrogram,
                progress_args=(
                    "Uploading file as Streamable Video...\nPlease wait!",
                    qmsg,
                    time(),
                ),
            )
            forward_vid = await sent_vid.forward(Vars.MESSAGE_DUMP)
        elif upload_type == "file":
            sent_vid = await c.send_document(
                chat_id=qmsg.chat.id,
                document=output_vid,
                caption=caption,
                thumb=video_thumbnail,
                reply_markup=Constants.support_kb,
                progress=progress_for_pyrogram,
                progress_args=(
                    "Uploading file as Telegram Document...\nPlease wait!",
                    qmsg,
                    time(),
                ),
            )
            forward_vid = await sent_vid.forward(Vars.MESSAGE_DUMP)
        elif upload_type == "streamtape":
            LocalDB.deldb()
            LocalDB.set("working", False)
            forward_vid = await streamtape_upload(
                qmsg,
                output_vid,
                file_size,
                video_thumbnail,
                logs_msg,
                public_log,
                user_id,
            )

    except Exception as err:
        LOGGER.error(f"Unable to Upload Video: {err}")
        LOGGER.error(format_exc())
        await qmsg.edit_text(
            f"#ERROR: Unable to Upload Video!\n\n**Error:** `{err}`",
        )
        await logs_msg.edit_text(
            f"#ERROR: Unable to Upload Video!\n\n**Error:** `{err}`",
        )
        await public_log.delete()
        await delete_trash(output_vid)
        await delete_all()
        return
    await delete_trash(output_vid)
    await delete_all()
    await qmsg.delete()
    db.set_usage()
    await public_log.edit_text(
        f"#WATERMARK_ADDED: Video Uploaded!\n\n**UserID:** `{user_id}`",
    )
    await logs_msg.delete()
    await c.send_message(
        chat_id=Vars.MESSAGE_DUMP,
        text=f"#WATERMARK_ADDED: Video Uploaded!\n\n{user_info}",
        reply_to_message_id=forward_vid.id,
        reply_markup=Constants.ban_kb(user_id),
    )
    return
