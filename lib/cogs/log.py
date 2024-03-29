import warnings

from discord.ext.commands import Cog
from lib.db import db_postgresql as db
from discord import Message

'''
ONLY ENABLE THIS IF DATABASE STORAGE PERMITS

I'm no longer updating this, maybe I'll make it log message history in a channel someday
I used the bot on 2 servers for 1 month and filled 10 000 rows of my database
'''


class Log(Cog):
    def __init__(self, bot):
        warnings.warn("Message logging enabled")
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("Log cog ready")

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if not after.author.bot and before.content != after.content:
            time = after.edited_at.strftime("%d/%m/%Y [%H:%M:%S]")
            db.execute(
                "INSERT INTO messages (MessageID, guild, channel, author, time, message, status) VALUES (%s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (MessageID) "
                "DO UPDATE SET "
                "   time = %s, "
                "   status = %s, "
                "   message = %s",
                after.id, after.guild.name, after.channel.name, after.author.name, time, after.content, "EDITED",
                time, "EDITED", after.content)

    @Cog.listener()
    async def on_message_delete(self, message: Message):
        if not message.author.bot:
            time = message.created_at.strftime("%d/%m/%Y [%H:%M:%S]")
            db.execute(
                "INSERT INTO messages (MessageID, guild, channel, author, time, message, status) VALUES (%s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (MessageID) "
                "DO UPDATE SET "
                "   time = %s, "
                "   status = %s",
                message.id, message.guild.name, message.channel.name, message.author.name, time, message.content,
                "DELETED",
                time, "DELETED")

    @Cog.listener()
    async def on_message(self, message: Message):
        if not message.author.bot:
            time = message.created_at.strftime("%d/%m/%Y [%H:%M:%S]")
            db.execute(
                "INSERT INTO messages (MessageID, guild, channel, author, time, message, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                message.id, message.guild.name, message.channel.name, message.author.name, time, message.content,
                "ORIGINAL")


def setup(bot):
    bot.add_cog(Log(bot))
