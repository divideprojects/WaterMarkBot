from os import getcwd

from prettyconf import Configuration
from prettyconf.loaders import EnvFile, Environment

env_file = f"{getcwd()}/.env"
config = Configuration(loaders=[Environment(), EnvFile(filename=env_file)])


class Vars:
    PUBLIC_LOGS = int(config("PUBLIC_LOGS", default=-100))
    WORKERS = int(config("WORKERS", default=16))
    DOWN_PATH = f"{getcwd()}/dpwatermarkbot/downloads"
    CACHE_TIME = int(config("CACHE_TIME", default=5))
    BOT_TOKEN = config("BOT_TOKEN")
    BOT_ID = BOT_TOKEN.split(":")[0]
    APP_ID = int(config("API_ID", default=12345))
    API_HASH = config("API_HASH")
    STREAMTAPE_API_PASS = config("STREAMTAPE_API_PASS")
    STREAMTAPE_API_USERNAME = config("STREAMTAPE_API_USERNAME")
    MESSAGE_DUMP = int(config("MESSAGE_DUMP"))
    PREFIX_HANDLER = config("PREFIX_HANDLER", default="/ !").split()
    SUPPORT_GROUP = config("SUPPORT_GROUP", default="@DivideSupport")
    AUTH_CHANNEL = config("AUTH_CHANNEL", default="@DivideProjects")
    PRESET = config("PRESET", default="ultrafast")
    OWNER_ID = int(config("OWNER_ID", default=777000))
    CAPTION = config("CAPTION", default="By @DivideProjects")
    DB_URI = config("DB_URI", default=None)
    VERSION = config("VERSION", default="v1.1 - Stable")
    BOT_USERNAME = config("BOT_USERNAME", default="DP_WaterMarkBot")
    STREAMTAPE_DEFAULT = config("STREAMTAPE_DEFAULT", default=None, cast=config.boolean)
    LIMIT_CPU = config("LIMIT_CPU", default=None, cast=config.boolean)
    LIMIT_USER_USAGE = config("JOIN_CHECK", default=None, cast=config.boolean)
    MAX_NON_JOIN_USAGE = config("MAX_NON_JOIN_USAGE", default=2)
    MAX_JOIN_USAGE = config("MAX_JOIN_USAGE", default=5)
