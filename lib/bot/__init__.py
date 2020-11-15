from discord.ext.commands import Bot as BaseBot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from ..db import db
import os

PREFIX = '/'
OWNER_IDS = [164144088818515968]
COGS = []

for filename in os.listdir('./lib/cogs'):
    if filename.endswith('.py'):
        COGS.append(f'lib.cogs.{filename[:-3]}')


def get_current_time():
    return datetime.now().strftime("[%H:%M:%S]")


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

        print(get_current_time(), "Bot is running")

        super().run(self.token, reconnect=True)

    async def print_message(self):
        channel = self.get_channel(636378952025374794)
        await channel.send("Test print message")

    async def on_connect(self):
        print(get_current_time(), "Logged in as {0.user}".format(self))

    async def on_disconnect(self):
        print(get_current_time(), "Bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == 'on_command_error':
            print(get_current_time(), "Something went wrong")
        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            await ctx.send("Command not found")
        elif hasattr(exc, 'original'):
            raise exc.original
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.guild = self.get_guild(636310389797290024)
            self.scheduler.add_job(self.print_message, CronTrigger(second="0,15,30,45"))
            self.scheduler.start()
            for cog in COGS:
                self.load_extension(cog)
                print(get_current_time(), f'Loaded cog: {cog}')
            print(get_current_time(), "Bot is ready")
        else:
            print(get_current_time(), "Bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
