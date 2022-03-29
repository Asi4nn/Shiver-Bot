"""
This file for storing functions to contain SQL queries to not pollute the rest of the bot code with
ugly query strings
"""
from typing import List, Tuple, Union
from lib.db import db_postgresql as db
from sqlalchemy.exc import SQLAlchemyError


def set_channel(guild_id: int, channel_id: int) -> bool:
    """
    Add or updates a channel in the channels table
    :param guild_id: int
    :param channel_id: int
    :return: Whether the channel was added or updated successfully
    """
    try:
        db.execute("INSERT INTO channels(GuildID, channel) "
                   "VALUES (%s, %s) "
                   "ON CONFLICT(GuildID) "
                   "DO UPDATE SET channel = %s",
                   guild_id, channel_id, channel_id)
        return True
    except SQLAlchemyError as e:
        print(e)
        return False


def set_command_channel(guild_id: int, channel_id: int) -> bool:
    """
    Add or updates a command channel in the channels table
    :param guild_id: int
    :param channel_id: int
    :return: Whether the channel was added or updated successfully
    """
    try:
        db.execute("INSERT INTO channels(GuildID, cmdchannel) "
                   "VALUES (%s, %s) "
                   "ON CONFLICT(GuildID) "
                   "DO UPDATE SET cmdchannel = %s",
                   guild_id, channel_id, channel_id)
        return True
    except SQLAlchemyError as e:
        print(e)
        return False


def remove_command_channel(guild_id: int) -> bool:
    """
    Removes command channel for the guild in the channels table
    :param guild_id: int
    :return: Whether the channel was removed successfully
    """
    try:
        db.execute("INSERT INTO channels(GuildID, cmdchannel) "
                   "VALUES (%s, NULL) "
                   "ON CONFLICT(GuildID) "
                   "DO UPDATE SET cmdchannel = NULL",
                   guild_id)
        return True
    except SQLAlchemyError as e:
        print(e)
        return False


def get_announcement_channel(guild_id: int) -> Union[int, None]:
    """
    Get announcement channel for the guild in the channels table
    :param guild_id: int
    :return: id of the channel or None if not found
    """
    try:
        return db.field("SELECT channel FROM channels WHERE GuildID = %s", guild_id)
    except SQLAlchemyError as e:
        print(e)
        return None


def get_command_channel(guild_id: int) -> Union[int, None]:
    """
    Get command channel for the guild in the channels table
    :param guild_id: int
    :return: id of the channel or None if not found
    """
    try:
        return db.field("SELECT cmdchannel FROM channels WHERE GuildID = %s", guild_id)
    except SQLAlchemyError as e:
        print(e)
        return None


def get_birthdays() -> List[Tuple[int, int, str]]:
    """
    Get all birthday records in the form: (UserID, GuildID, date)
    :return: records of all birthdays
    """
    return db.records("SELECT * FROM birthdays")


def get_guild_birthdays(guild_id) -> List[Tuple[int, int, str]]:
    """
    Get all birthday records for the given guild in the form: (UserID, GuildID, date)
    :return: records of all birthdays
    """
    return db.records("SELECT * FROM birthdays WHERE GuildID = %s", guild_id)


def get_birthday_record(user_id, guild_id) -> Union[None, Tuple[int, int, str]]:
    return db.record("SELECT * FROM birthdays WHERE UserID = %s AND GuildID = %s", user_id, guild_id)


def set_birthday(user_id: int, guild_id: int, date: str) -> bool:
    """
    Add or updates a birthday in the birthdays table
    :param user_id: int
    :param guild_id: int
    :param date: str
    :return: Whether the birthday was added or updated successfully
    """
    try:
        db.execute("INSERT INTO birthdays(UserID, GuildID, date) "
                   "VALUES (%s, %s, %s) "
                   "ON CONFLICT(UserID, GuildId) "
                   "DO UPDATE SET date = %s",
                   user_id, guild_id, date, date)
        return True
    except SQLAlchemyError as e:
        print(e)
        return False
