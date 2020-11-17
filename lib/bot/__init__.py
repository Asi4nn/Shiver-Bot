
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from asyncio import sleep
from datetime import datetime

from discord.ext.commands import Bot as BaseBot
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument)
from discord.errors import HTTPException, Forbidden

from ..helpers.getTime import get_current_time
from ..db import db

import os

PREFIX = '/'
OWNER_IDS = [164144088818515968]
COGS = []
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

for filename in os.listdir('./lib/cogs'):
    if filename.endswith('.py'):
        COGS.append(f'lib.cogs.{filename[:-3]}')


class Bot(BaseBot):
    def __init__(self):
        self.ready = False
        self.prefix = PREFIX
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)
        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS)

    def run(self):
        with open('lib/bot/TOKEN.txt', 'r', encoding="utf-8") as token:
            self.token = token.read()

        self.load_cogs()

        print(get_current_time(), "Bot is running")

        super().run(self.token, reconnect=True)

    def load_cogs(self):
        for cog in COGS:
            self.load_extension(cog)
            print(get_current_time(), f'Loaded cog: {cog}')

    async def print_message(self):
        channel = self.get_channel(636378952025374794)
        await channel.send("Hourly message trigger")

    async def on_connect(self):
        print(get_current_time(), "Logged in as {0.user}".format(self))

    async def on_disconnect(self):
        print(get_current_time(), "Bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == 'on_command_error':
            print(get_current_time(), "Something went wrong")
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("Argument(s) are missing from command")
        elif isinstance(exc.original, HTTPException):
            await ctx.send("Unable to send message (likely too long)")
        elif isinstance(exc.original, Forbidden):
            await ctx.send("I don't have permission to do that")
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(636310389797290024)
            self.scheduler.add_job(self.print_message, CronTrigger(second="0", minute="0"))
            self.scheduler.start()

            self.ready = True
            print(get_current_time(), "Bot is ready")
        else:
            print(get_current_time(), "Bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
