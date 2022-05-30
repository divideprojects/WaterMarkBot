from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageNotModified
from pyrogram.types import CallbackQuery

from dpwatermarkbot import LOGGER
from dpwatermarkbot.bot_class import DPWaterMarkBot
from dpwatermarkbot.db import MainDB
from dpwatermarkbot.utils.build_kb import gen_position_kb, gen_size_kb
from dpwatermarkbot.utils.constants import Constants
from dpwatermarkbot.utils.ikb import ikb
from dpwatermarkbot.vars import Vars


@DPWaterMarkBot.on_callback_query(filters.regex("^btn_not_work$"))
async def btn_not_work_callback(_, q: CallbackQuery):
    await q.answer(
        "Well, this button does not work xD\n\nCheck other buttons!",
        show_alert=True,
    )


@DPWaterMarkBot.on_callback_query(filters.regex("^custom_thumb."))
async def custom_thumb_callback(_, q: CallbackQuery):
    qdata = q.data.split(".")[1]
    txt = ""
    if qdata == "already":
        txt = "A custom thumbnail has already been set, to remove it use /delthumb command!"
    elif qdata == "none":
        txt = "A custom thumbnail has not been set, to set, use /savethumb as a reply to a picture!"
    await q.answer(txt, show_alert=True)


@DPWaterMarkBot.on_callback_query(filters.regex("^ban_"))
async def ban_user(c: DPWaterMarkBot, q: CallbackQuery):
    user_id = int(q.data.split("_", 1)[1])
    await c.ban_chat_member(Vars.AUTH_CHANNEL, user_id)
    await q.answer("User Banned from Updates Channel!", show_alert=True)


@DPWaterMarkBot.on_callback_query(filters.regex("^menu_size$"))
async def menu_size(_, q: CallbackQuery):
    db = MainDB(q.from_user.id)
    size_tag = db.get_size()
    kb = await gen_size_kb(
        5,
        7,
        10,
        15,
        20,
        25,
        30,
        35,
        40,
        45,
        50,
        btn_per_line=4,
        size_tag=str(size_tag),
    )
    await q.message.edit_text(
        "Here you can set custom size for Watermark!",
        reply_markup=ikb(kb),
    )
    await q.answer()


@DPWaterMarkBot.on_callback_query(filters.regex("^main.settings$"))
async def menu_settings(_, q: CallbackQuery):
    await q.message.edit_text(
        "Click on the buttons below to change Settings:",
        disable_web_page_preview=True,
        reply_markup=ikb(
            (await Constants.settings_kb(q.from_user.id)),
        ),
    )
    await q.answer()


@DPWaterMarkBot.on_callback_query(filters.regex("^menu_position$"))
async def menu_position(_, q: CallbackQuery):
    db = MainDB(q.from_user.id)
    watermark_position = db.get_position()
    watermark_dict = {
        "5:main_h-overlay_h": "Bottom Left",
        "main_w-overlay_w-5:main_h-overlay_h-5": "Bottom Right",
        "main_w-overlay_w-5:5": "Top Right",
        "5:5": "Top Left",
    }
    position_tag = watermark_dict[watermark_position]
    kb = await gen_position_kb(position_tag)
    await q.message.edit_text(
        "Here you can set custom position for Watermark!",
        reply_markup=ikb(kb),
    )
    await q.answer()


@DPWaterMarkBot.on_callback_query(filters.regex("^set_size_"))
async def menu_size_m(c: DPWaterMarkBot, q: CallbackQuery):
    # Meh gay AF ...
    db = MainDB(q.from_user.id)
    cb_data = q.data

    await c.send_message(
        chat_id=Vars.MESSAGE_DUMP,
        text=f"#SETTINGS_SET: [{q.from_user.first_name}](tg://user?id={q.from_user.id}) Changed Settings!\n\n**User "
        f"ID:** #id{q.from_user.id}\n**Data:** `{cb_data}`",
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=Constants.ban_kb(q.from_user.id),
    )

    new_position = cb_data.split("_", 2)[2]
    db.set_size(new_position)

    try:
        await q.message.edit(
            text="Here you can set your Watermark Settings:",
            disable_web_page_preview=True,
            reply_markup=ikb(
                (await Constants.settings_kb(q.from_user.id)),
            ),
        )
    except MessageNotModified as ef:
        LOGGER.warning(str(ef))

    await q.answer(f"Set Watermark Size to {new_position}", show_alert=True)


@DPWaterMarkBot.on_callback_query(filters.regex("^set_position_"))
async def menu_position_m(c: DPWaterMarkBot, q: CallbackQuery):
    cb_data = q.data
    db = MainDB(q.from_user.id)

    await c.send_message(
        chat_id=Vars.MESSAGE_DUMP,
        text=f"#SETTINGS_SET: [{q.from_user.first_name}](tg://user?id={q.from_user.id}) Changed Settings!\n\n**User "
        f"ID:** #id{q.from_user.id}\n**Data:** `{cb_data}`",
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=Constants.ban_kb(q.from_user.id),
    )
    new_position = cb_data.split("_", 2)[2]

    db.set_position(new_position)

    try:
        await q.message.edit(
            text="Here you can set your Watermark Settings:",
            disable_web_page_preview=True,
            reply_markup=ikb(
                (await Constants.settings_kb(q.from_user.id)),
            ),
        )
    except MessageNotModified as ef:
        LOGGER.warning(str(ef))

    await q.answer(f"Set Watermark Position to {new_position}", show_alert=True)


@DPWaterMarkBot.on_callback_query(filters.regex("^help_callback."))
async def help_callback_func(_, q: CallbackQuery):
    qdata = q.data.split(".")[1]
    if qdata in ("start", "page1"):
        await q.message.edit_text(
            Constants.page1_help,
            reply_markup=ikb(Constants.page1_help_kb),
            disable_web_page_preview=True,
        )
    elif qdata == "page2":
        await q.message.edit_text(
            Constants.page2_help,
            reply_markup=ikb(Constants.page2_help_kb),
            disable_web_page_preview=True,
        )
    await q.answer()
