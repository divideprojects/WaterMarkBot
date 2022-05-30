from asyncio import create_subprocess_exec, sleep, subprocess
from math import floor
from os import path
from random import randint
from re import findall
from time import time
from traceback import format_exc

from humanfriendly import format_timespan
from PIL import Image
from psutil import cpu_count
from pyrogram.errors import FloodWait, MessageNotModified

from dpwatermarkbot import LOGGER
from dpwatermarkbot.db import LocalDB
from dpwatermarkbot.utils.display_progress import time_formatter
from dpwatermarkbot.utils.ikb import ikb
from dpwatermarkbot.vars import Vars


async def vidmark(
    the_media,
    message,
    watermark_path,
    output_vid,
    total_time,
    logs_msg,
    mode,
    position,
    size,
    user_id,
    public_log,
):
    num_threads = (
        (round(cpu_count() / 2) if round(cpu_count() / 2) == 0 else 1)
        if Vars.LIMIT_CPU
        else cpu_count()
    )
    working_dir = f"{Vars.DOWN_PATH}/{user_id}/progress.txt"
    file_genertor_command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "quiet",
        "-progress",
        working_dir,
        "-i",
        the_media,
        "-i",
        watermark_path,
        "-filter_complex",
        f"[1][0]scale2ref=w='iw*{size}/100':h='ow/mdar'[wm][vid];[vid][wm]overlay={position}",
        "-c:v",
        "h264",
        "-threads",
        str(num_threads),
        "-preset",
        mode,
        "-tune",
        "film",
        "-c:a",
        "copy",
        output_vid,
    ]
    process = await create_subprocess_exec(
        *file_genertor_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    LocalDB.set("pid", process.pid)
    cancel_kb = ikb([[("Cancel ❌", f"cancel_pid.{user_id}")]])

    try:
        while process.returncode != 0:
            await sleep(5)
            with open(working_dir, "r+") as file:
                text = file.read()
                frame = findall(r"frame=(\d+)", text)
                time_in_us = findall(r"out_time_ms=(\d+)", text)
                progress = findall(r"progress=(\w+)", text)
                speed = findall(r"speed=(\d+\.?\d*)", text)
                int(frame[-1]) if frame else 1
                speed = speed[-1] if speed else 1
                time_in_us = time_in_us[-1] if time_in_us else 1
                if progress and progress[-1] == "end":
                    break
                elapsed_time = int(time_in_us) / 1000000
                difference = floor((total_time - elapsed_time) / float(speed))
                eta = "-"
                if difference > 0:
                    eta = time_formatter(difference * 1000)
                percentage = floor(elapsed_time * 100 / total_time)
                progress_str = "📊 **Progress:** {}%\n`[{}{}]`".format(
                    round(percentage, 2),
                    "".join("▓" for _ in range(floor(percentage / 10))),
                    "".join("░" for _ in range(10 - floor(percentage / 10))),
                )

                stats = (
                    f"📦️ **Adding Watermark [Preset: `{mode}`]**\n\n"
                    f"⏰️ **ETA:** `{eta}`\n"
                    f"❇️ **Position:** `{position}`\n"
                    f"🔰 **PID:** `{process.pid}`\n🔄"
                    f"**Duration: `{format_timespan(total_time)}`**\n\n"
                    f"{progress_str}\n"
                )
                try:
                    await logs_msg.edit(text=stats, reply_markup=cancel_kb)
                    await public_log.edit(stats)
                    await message.edit(text=stats, reply_markup=cancel_kb)
                except MessageNotModified:
                    pass
                except FloodWait as e:
                    await sleep(e.value)
                except Exception as ef:
                    LOGGER.error(ef)
    except (FileNotFoundError, Exception):
        stats = "Adding watermark to Video, please wait..."
        try:
            await logs_msg.edit(text=stats, reply_markup=cancel_kb)
            await public_log.edit(stats)
            await message.edit(text=stats, reply_markup=cancel_kb)
        except MessageNotModified:
            pass
        except FloodWait as e:
            await sleep(e.value)
        except Exception as ef:
            LOGGER.error(ef)
            LOGGER.error(format_exc())
            return None

    _, stderr = await process.communicate()
    err_response = stderr.decode().strip()
    if err_response:
        LOGGER.error(err_response)
        return None
    if path.lexists(output_vid):
        return output_vid
    return None


async def gen_ss(user_id, duration, output_vid, width, height):
    try:
        video_thumbnail = f"{Vars.DOWN_PATH}/{user_id}/{int(time())}.jpg"
        ttl = randint(0, int(duration) - 1)
        file_genertor_command = [
            "ffmpeg",
            "-ss",
            str(ttl),
            "-i",
            output_vid,
            "-vframes",
            "1",
            video_thumbnail,
        ]
        process = await create_subprocess_exec(
            *file_genertor_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        if e_response:
            LOGGER.error(e_response)
        t_response = stdout.decode().strip()
        if t_response:
            LOGGER.error(t_response)
        Image.open(video_thumbnail).convert("RGB").save(video_thumbnail)
        img = Image.open(video_thumbnail)
        img.resize((width, height))
        img.save(video_thumbnail, "JPEG")
        return video_thumbnail
    except Exception as err:
        LOGGER.error(f"Error: {err}")
        LOGGER.error(format_exc())
