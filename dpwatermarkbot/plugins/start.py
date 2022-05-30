from pyrogram import filters
from pyrogram.types import Message

from dpwatermarkbot.bot_class import DPWaterMarkBot
from dpwatermarkbot.utils.constants import Constants
from dpwatermarkbot.utils.ikb import ikb
from dpwatermarkbot.utils.joinCheck import joinCheck
from dpwatermarkbot.vars import Vars


@DPWaterMarkBot.on_message(
    filters.command("start", Vars.PREFIX_HANDLER) & filters.private,
)
@joinCheck()
async def start_bot(_, m: Message):
    return await m.reply_text(
        Constants.start_msg.format(m.from_user.first_name, Vars.CAPTION),
        reply_markup=ikb(Constants.START_KB),
        disable_web_page_preview=True,
        quote=True,
    )


@DPWaterMarkBot.on_message(
    filters.command("help", Vars.PREFIX_HANDLER) & filters.private,
)
@joinCheck()
async def help_bot(_, m: Message):
    return await m.reply_text(
        Constants.page1_help,
        reply_markup=ikb(Constants.page1_help_kb),
        disable_web_page_preview=True,
    )
