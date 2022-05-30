from pyrogram import filters
from pyrogram.types import Message

from dpwatermarkbot.bot_class import DPWaterMarkBot
from dpwatermarkbot.utils.constants import Constants
from dpwatermarkbot.utils.ikb import ikb
from dpwatermarkbot.utils.joinCheck import joinCheck


@DPWaterMarkBot.on_message(filters.command("settings") & filters.private)
@joinCheck()
async def settings_bot(_, m: Message):
    await m.reply_text(
        "Click on the buttons below to change Settings:",
        disable_web_page_preview=True,
        reply_markup=ikb(await Constants.settings_kb(m.from_user.id)),
        quote=True,
    )
