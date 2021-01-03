from discord.ext.commands import Cog
from ..db import db
from discord import Message

class Log(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        pass

    @Cog.listener()
    async def on_message_edit(self, before:Message, after:Message):
        if not after.author.bot:
            time = after.edited_at.strftime("%D/%M/%Y [%H:%M:%S]")
            db.execute("INSERT OR REPLACE INTO messages (MessageID, guild, channel, author, time, message, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       after.id, after.guild.name, after.channel.name, after.author.name, time, after.content, "EDITED")

    @Cog.listener()
    async def on_message_delete(self, message: Message):
        if not message.author.bot:
            time = message.created_at.strftime("%D/%M/%Y [%H:%M:%S]")
            db.execute("INSERT OR REPLACE INTO messages (MessageID, guild, channel, time, author, message, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       message.id, message.guild.name, message.channel.name, message.author.name, time, message.content, "DELETED")

    @Cog.listener()
    async def on_message(self, message: Message):
        if not message.author.bot:
            created = message.created_at
            time = message.created_at.strftime("%D/%M/%Y [%H:%M:%S]")
            db.execute("INSERT OR REPLACE INTO messages (MessageID, guild, channel, author, time, message, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       message.id, message.guild.name, message.channel.name, message.author.name, time, message.content, "MESSAGE")


def setup(bot):
    bot.add_cog(Log(bot))
