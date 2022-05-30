from datetime import datetime
from typing import Any, Dict, List

from pickledb_ujson import load

from dpwatermarkbot import LOGGER
from dpwatermarkbot.db.mongo import MongoDB
from dpwatermarkbot.vars import Vars

# Local database from pickledb
LocalDB = load(f"{Vars.BOT_USERNAME}_local.db", True)
LocalDB.set("working", False)


class MainDB(MongoDB):
    """
    Class to manage collection of bot in MongoDB
    """

    # bot username, which will be used as collection name
    db_name = Vars.BOT_USERNAME

    def __init__(self, user_id: int) -> None:
        """
        initialise the class MainDB by passing a user_id to get user_info
        """
        super().__init__(MainDB.db_name)
        self.user_id = user_id
        self.user_info = self.__ensure_in_db()  # get user_info from database

    def get_info(self) -> Dict[str, Any]:
        """
        Function used to get info about a certain user
        """
        return self.user_info

    def set_position(self, watermark_position) -> None:
        """
        Set position of watermark for user
        """
        self.update(
            {"_id": self.user_id},
            {"watermark_position": watermark_position},
        )
        return

    def get_position(self) -> str:
        """
        Get position of watermark for user
        """
        return self.user_info.get("watermark_position", "5:5")

    def get_plan(self) -> str:
        """
        Get plan of user
        """
        return self.user_info.get("plan", "free")

    def set_usage(
        self,
        update_date=datetime.utcnow().date(),
        usage_value: int = 1,
    ) -> None:
        """
        Set usage of user
        """
        self.update(
            {"_id": self.user_id},
            {
                "usage": self.user_info.get("usage", {})
                | {str(update_date): self.get_usage() + usage_value},
            },
        )
        return

    def get_usage(self, date_today=datetime.utcnow().date()) -> int:
        """
        Get usage of user
        """
        return self.user_info.get("usage", {}).get(str(date_today), 0)

    def set_size(self, watermark_size) -> None:
        """
        Set size of watermark for user
        """
        self.update({"_id": self.user_id}, {"watermark_size": watermark_size})
        return

    def get_size(self) -> int:
        """
        Get size of watermark for user
        """
        return self.user_info.get("watermark_size", 7)

    def set_watermark(self, file_id) -> None:
        """
        Set watermark image for user
        """
        self.update({"_id": self.user_id}, {"watermark_fileid": file_id})
        return

    def get_watermark(self) -> str:
        """
        Get watermark image for user
        """
        return self.user_info.get("watermark_fileid", None)

    @staticmethod
    def get_all_users() -> List[int]:
        """
        This function is used to get all the users stored in database
        """
        users = MongoDB(MainDB.db_name).find_all()
        return [user["_id"] for user in users]

    @staticmethod
    def total_users_count() -> int:
        """
        This function is used to count all the users stored in database
        """
        return MongoDB(MainDB.db_name).count()

    @staticmethod
    def delete_user(user_id: int) -> None:
        """
        This function deletes the user from database
        """
        return MongoDB(MainDB.db_name).delete_one({"_id": user_id})

    def __ensure_in_db(self) -> Dict[str, Any]:
        """
        This function ensures that the user is already in db and fixes data to latest schema
        """
        user_data = self.find_one({"_id": self.user_id})
        if not user_data:
            user_data = {
                "_id": self.user_id,  # user id of user
                "watermark_position": "5:5",  # default watermark position
                "watermark_fileid": None,  # default watermark file
                "watermark_size": 7,  # default watermark size
                "join_date": datetime.now(),  # Joining date of user with time
                "usage": {},  # List of usage of user
            }
            self.insert_one(user_data)
            LOGGER.info(f"Initialized New User: {self.user_id}")
        return user_data
