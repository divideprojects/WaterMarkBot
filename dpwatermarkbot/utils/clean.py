from os import remove
from shutil import rmtree
from traceback import format_exc

from dpwatermarkbot.vars import Vars


async def delete_trash(file: str):
    try:
        remove(file)
    except OSError:
        format_exc()


async def delete_all():
    try:
        rmtree(f"{Vars.DOWN_PATH}/")
    except OSError:
        format_exc()
