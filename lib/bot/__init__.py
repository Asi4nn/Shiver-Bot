from apscheduler.schedulers.asyncio import AsyncIOScheduler
from os import listdir, environ
from dotenv import load_dotenv

from discord.ext.commands import Bot as BaseBot
from discord.ext.commands import when_mentioned_or
from discord.ext.commands import (CommandNotFound, BadArgument)

from discord import Game, Intents

from ..helpers.getTime import get_current_time
from ..db import bot_queries
from typing import Union


load_dotenv()

TOKEN = environ['TOKEN'].strip()
USE_DB = environ['USE_DB'].strip() == 'true'
PREFIX = '$'
OWNER_IDS = [164144088818515968]
COGS = []
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

for filename in listdir('./lib/cogs'):
    if filename.endswith('.py') and filename[:-3] != "log":  # disable message logging for saving db storage
        COGS.append(f'lib.cogs.{filename[:-3]}')


def get_prefix(client, message):
    return when_mentioned_or(PREFIX)(client, message)


class Bot(BaseBot):
    def __init__(self):
        self.ready = False
        self.prefix = PREFIX
        self.scheduler = AsyncIOScheduler()
        self.token = None

        super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS, intents=Intents.all())

    def run(self):
        self.token = TOKEN
        self.load_cogs()

        print(get_current_time(), "Bot is running")

        super().run(self.token, reconnect=True)

    def load_cogs(self):
        for cog in COGS:
            self.load_extension(cog)
            print(get_current_time(), f'Loaded cog: {cog}')

    def get_announcement_channel(self, guild_id) -> Union[int, None]:
        return bot_queries.get_announcement_channel(guild_id)

    def get_command_channel(self, guild_id) -> Union[int, None]:
        return bot_queries.get_command_channel(guild_id)

    async def on_connect(self):
        print(get_current_time(), "Logged in as {0.user}".format(self))

    async def on_disconnect(self):
        print(get_current_time(), "Bot disconnected")

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            print(get_current_time(), "Bot is ready")
            await self.change_presence(activity=Game(f"{PREFIX}help"))
        else:
            print(get_current_time(), "Bot reconnected")

    # YOU NEED THIS FOR COMMANDS TO WORK
    async def on_message(self, message):
        if message.author.bot:
            return

        command_channel_id = self.get_command_channel(message.guild.id)
        if command_channel_id and message.channel.id != command_channel_id:
            return

        await self.process_commands(message)


bot = Bot()
