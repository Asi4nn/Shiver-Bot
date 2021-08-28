from discord.ext.commands import Cog
from lib.db import db_postgresql as db
from discord import Message


class Log(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        pass

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if not after.author.bot:
            time = after.edited_at.strftime("%d/%m/%Y [%H:%M:%S]")
            db.execute(
                "INSERT INTO messages (MessageID, guild, channel, author, time, message, status) VALUES (?, ?, ?, ?, ?, ?, ?) "
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
                message.id, message.guild.name, message.channel.name, message.author.name, time, message.content, "DELETED",
                time, "DELETED")

    @Cog.listener()
    async def on_message(self, message: Message):
        if not message.author.bot:
            time = message.created_at.strftime("%d/%m/%Y [%H:%M:%S]")
            db.execute(
                "INSERT INTO messages (MessageID, guild, channel, author, time, message, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                message.id, message.guild.name, message.channel.name, message.author.name, time, message.content, "ORIGINAL")


def setup(bot):
    bot.add_cog(Log(bot))
