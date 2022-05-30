from logging import INFO, WARNING, basicConfig, getLogger
from sys import exit as sysexit
from sys import version_info
from time import time
from traceback import format_exc

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=INFO,
)

getLogger("pyrogram").setLevel(WARNING)
LOGGER = getLogger(__name__)

# if version < 3.9, stop bot.
if version_info[0] < 3 or version_info[1] < 9:
    LOGGER.error(
        (
            "You MUST have a Python Version of at least 3.9!\n"
            "Multiple features depend on this. Bot quitting."
        ),
    )
    sysexit(1)  # Quit the Script

# the secret configuration specific things
try:
    from .vars import Vars
except Exception as ef:
    LOGGER.error(ef)  # Print Error
    LOGGER.error(format_exc())
    sysexit(1)

LOGGER.info("------------------------")
LOGGER.info("|    DP_WaterMarkBot    |")
LOGGER.info("------------------------")
LOGGER.info(f"Version: {Vars.VERSION}")
LOGGER.info(f"Owner: {str(Vars.OWNER_ID)}\n")

UPTIME = time()  # Check bot uptime
