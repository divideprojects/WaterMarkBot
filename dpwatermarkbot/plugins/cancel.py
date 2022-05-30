from os import kill
from traceback import format_exc

from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from dpwatermarkbot import LOGGER
from dpwatermarkbot.bot_class import DPWaterMarkBot
from dpwatermarkbot.db import LocalDB
from dpwatermarkbot.utils.clean import delete_all
from dpwatermarkbot.utils.joinCheck import joinCheck
from dpwatermarkbot.vars import Vars


@DPWaterMarkBot.on_message(filters.command("cancel") & filters.private)
@joinCheck()
async def cancel_watermark_adder(c: DPWaterMarkBot, m: Message):
    if int(LocalDB.get("chat_id")) not in {m.from_user.id, Vars.OWNER_ID}:
        await m.reply_text("You don't have any current running process!")
        return

    msg = (
        "Watermark Adding Process stopped by Owner"
        if m.from_user.id == Vars.OWNER_ID
        else "Watermark Adding Process Stopped!"
    )

    if "pid" in LocalDB.getall():
        try:
            kill(LocalDB.get("pid"), 9)
        except ProcessLookupError:
            LOGGER.error(f"{LocalDB.get('pid')} Process not running!")
        except Exception as err:
            LOGGER.error(err)
            LOGGER.error(format_exc())

    await delete_all()
    await c.send_message(
        chat_id=Vars.MESSAGE_DUMP,
        text=f"#WATERMARK_ADDER: Stopped!\n**UserID:** #id{m.from_user.id}",
    )
    await m.reply_text(msg)
    try:
        await c.edit_message_text(
            chat_id=int(LocalDB.get("chat_id")),
            message_id=int(LocalDB.get("message")),
            text="🚦🚦 Last Process Stopped 🚦🚦",
        )
    except Exception as ef:
        LOGGER.error(ef)
        LOGGER.error(format_exc())

    return


@DPWaterMarkBot.on_callback_query(filters.regex("^cancel_"))
async def cancel_task(c: DPWaterMarkBot, q: CallbackQuery):
    ctype = q.data.split("_")[1]
    user_id = int(q.data.split(".", 1)[1])

    if ctype.startswith("_add"):
        await q.message.edit_text("Process Cancelled 🚦🚦")

    elif ctype.startswith("_pid"):
        if "pid" in LocalDB.getall():
            try:
                kill(LocalDB.get("pid"), 9)
            except ProcessLookupError:
                LOGGER.error(f"{LocalDB.get('pid')} Process not running!")
            except Exception as err:
                LOGGER.error(err)
                LOGGER.error(format_exc())

        await delete_all()
        await c.send_message(
            chat_id=Vars.MESSAGE_DUMP,
            text=f"#WATERMARK_ADDER: Stopped!\n**UserID:** #id{user_id}",
        )
        try:
            await c.edit_message_text(
                chat_id=int(LocalDB.get("chat_id")),
                message_id=int(LocalDB.get("message")),
                text="🚦🚦 Last Process Stopped 🚦🚦",
            )
        except Exception as ef:
            LOGGER.error(ef)
            LOGGER.error(format_exc())

    await q.answer("Watermark Adding Process Stopped!")
    return
