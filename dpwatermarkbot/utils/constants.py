from pyrogram.types import Message

from dpwatermarkbot.db import MainDB
from dpwatermarkbot.utils.ikb import ikb
from dpwatermarkbot.vars import Vars


class Constants:
    @staticmethod
    async def settings_kb(user_id: int):
        db = MainDB(user_id)
        set_status = (
            ("Custom Thumbnail ✅", "custom_thumb.already")
            if (db.get_watermark())
            else ("Custom Thumbnail ❌", "custom_thumb.none")
        )
        return [
            [("Size", "menu_size")],
            [("Position", "menu_position")],
            [set_status],
        ]

    @staticmethod
    def ban_kb(user_id: int):
        return (
            ikb([[("Ban User", f"ban_{user_id}")]])
            if user_id != Vars.OWNER_ID
            else None
        )

    @staticmethod
    async def join_channel_msg(m: Message):
        join_channel = Vars.AUTH_CHANNEL.replace("@", "")
        return await m.reply_text(
            "You have reached your limit of usage."
            "\nPlease wait for some time before using this bot again."
            f"\nIf you want to increase the usage limit, join {Vars.AUTH_CHANNEL}",
            reply_markup=ikb(
                [[("Join Channel", f"https://t.me/{join_channel}", "url")]],
            ),
        )

    @staticmethod
    def get_user_usage(user_id: int) -> str:
        db = MainDB(user_id)
        return (
            "<b>ℹ️ Your Information</b>"
            f"\n\n<b>User ID:</b> <code>{user_id}</code>"
            f"\n<b>Usage Today:</b> {db.get_usage()}"
            f"\n<b>Plan</b>: {db.get_plan()}"
        )

    refresh_usage_kb = ikb([[("🔄 Refresh", "refresh_usage")]])

    public_logs_kb = [("Public Logs", "https://t.me/DP_WaterMarkBotLogs", "url")]

    START_KB = [
        [
            ("How to use", "help_callback.start"),
            ("Help & Support", f"https://t.me/{Vars.SUPPORT_GROUP}", "url"),
        ],
        public_logs_kb,
    ]
    page1_help_kb = [[(">>>", "help_callback.page2")]]
    page2_help_kb = [[("<<<", "help_callback.page1")]]

    start_msg = """
Hi {}, I am Video Watermark Adder Bot!

**How to Added Watermark to a Video?**
**Usage:** First Send a JPG Image/Logo, then send any Video. Better add watermark to a MP4 or MKV Video.

{}
"""

    page1_help = """
<b><u>Commands:</b></u>
/start: <i>Start the bot.</i>
/help: <i>Show this message.</i>
/cancel: <i>Cancel the current operation for user.</i>
/settings: <i>Set the watermark size and position.</i>
/mythumb: <i>Show your saved watermark!</i>
/delthumb: <i>Delete the current saved watermark.</i>
/savethumb (reply to photo): <i>Save the current photo as permanent photo.</i>
/myaccount: <i>Get information about your usage and plan.</i>

<b>Note:</b> You do not need to always set a watermark using /savethumb command, \
this is only used when you send a video without sending a watermark first!

You can check current status [here](https://t.me/DP_WaterMarkBotLogs)
"""
    page2_help = """
<b><u>FAQs</b></u>:

<b>• Why is bot slow?</b>
- <i>Bot is hosted on free heroku server, which ultimately makes it slow.</i>

<b>• Why is bot always busy?</b>
- <i>The bot can only process 1 video at a time, check 1st FAQ to know why.</i>

<b>• Why does the video size increase?</b>
- <i>The bot currently uses ultrafast algorithm of ffmpeg which results in higher file sizes, 1st FAQ to know more.</i>

<b>• Is NSFW allowed on Bot?</b>
- <i>No, any user found uploading and using NSFW Videos on Bot will be banned infinitely</i>

<b>• Why will happen if file size becomes more than 2GB?</b>
- <i>The video will be uploaded to streamtape and bot will send a link to you.</i>

<b>• Why is there a restriction of 5 minutes?</b>
- <i>For now bot is providing every services for free and that could be misused by spammers so inorder to maintain a stable performance all of the users are limited</i>
"""

    PROGRESS = """
Percentage : {0}%
Done ✅: {1}
Total 🌀: {2}
Speed 🚀: {3}/s
ETA 🕰: {4}
"""
    support_kb = ikb(
        [
            [
                ("Support Group", f"https://t.me/{Vars.SUPPORT_GROUP}", "url"),
                ("Bots Channel", "https://t.me/DivideProjects", "url"),
            ],
        ],
    )
