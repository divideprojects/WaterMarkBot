from pyrogram import filters
from pyrogram.types import Message

from dpwatermarkbot.bot_class import DPWaterMarkBot
from dpwatermarkbot.db import LocalDB, MainDB
from dpwatermarkbot.utils.constants import Constants
from dpwatermarkbot.utils.ikb import ikb
from dpwatermarkbot.vars import Vars


@DPWaterMarkBot.on_message(filters.private & filters.command("status"))
async def bot_status(_, m: Message):
    status = LocalDB.get("working")

    msg_text = (
        "Sorry, Currently I am busy with another Task!\nI can't add Watermark at this moment.\n\nCheck current status "
        "on Logs Channel by click the button below!"
        if status
        else "I am Free Now!\nSend me any video to add Watermark."
    )

    if int(m.from_user.id) == Vars.OWNER_ID:
        total_users = MainDB.total_users_count()
        msg_text += f"\n\n**Total Users in DB:** `{total_users}`"

    await m.reply_text(
        msg_text,
        reply_markup=ikb([Constants.public_logs_kb]),
        quote=True,
    )
    return
