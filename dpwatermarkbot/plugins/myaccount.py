from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from dpwatermarkbot.bot_class import DPWaterMarkBot
from dpwatermarkbot.utils.constants import Constants
from dpwatermarkbot.vars import Vars


@DPWaterMarkBot.on_message(
    filters.command("myaccount", Vars.PREFIX_HANDLER) & filters.private,
)
async def start_bot(_, m: Message):
    user_id = m.from_user.id
    return await m.reply_text(
        Constants.get_user_usage(user_id),
        reply_markup=Constants.refresh_usage_kb,
        quote=True,
    )


@DPWaterMarkBot.on_callback_query(filters.regex("^refresh_usage$") & filters.private)
async def refresh_usage(_, q: CallbackQuery):
    user_id = q.from_user.id
    return await q.message.edit_text(
        Constants.get_user_usage(user_id),
        reply_markup=Constants.refresh_usage_kb,
    )
