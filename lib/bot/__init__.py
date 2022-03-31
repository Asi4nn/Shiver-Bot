import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from discord.ext.commands import Bot as BaseBot
from discord.ext.commands import when_mentioned_or
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, MissingPermissions)
from discord.errors import HTTPException, Forbidden
from discord.utils import get

from ..helpers.getTime import get_current_time
from ..db import bot_queries
from typing import Union

from os import listdir, environ

import re

from dotenv import load_dotenv

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

        super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS, intents=discord.Intents.all())

    def run(self):
        self.token = TOKEN

        self.load_cogs()

        print(get_current_time(), "Bot is running")

        super().run(self.token, reconnect=True)

    def load_cogs(self):
        for cog in COGS:
            self.load_extension(cog)
            print(get_current_time(), f'Loaded cog: {cog}')

    async def announce_birthday(self, guild, channel, mention, age):
        send_channel = get(self.get_guild(guild).text_channels, id=channel)
        await send_channel.send(f":birthday: @here Happy Birthday to {mention} who's turning {age} today "
                                f"{':older_adult:' if age > 18 else ':baby:'}")

    def get_announcement_channel(self, guild_id) -> Union[int, None]:
        return bot_queries.get_announcement_channel(guild_id)

    def get_command_channel(self, guild_id) -> Union[int, None]:
        return bot_queries.get_command_channel(guild_id)

    async def birthday_trigger(self):
        bdays = bot_queries.get_birthdays()

        for record in bdays:
            if int(record[2][0:2]) == datetime.today().day and int(record[2][3:5]) == datetime.today().month:
                channel = self.get_announcement_channel(record[1])
                if channel is None:
                    general = discord.utils.get(bot.get_guild(record[1]).text_channels, name="general")
                    await general.send(f"Please set a announcement channel with {PREFIX}channel to use the birthday "
                                       "announcement feature")
                    break
                age = datetime.today().year - int(record[2][6:])
                await self.announce_birthday(record[1], channel, f'<@!{record[0]}>', age)

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
            # Checks if command looks like currency (matches numbers and periods)
            if not re.match(r'^\$[0-9\.]*$', ctx.message.content.split(' ', 1)[0]):
                await ctx.reply(f"Command not found, type {PREFIX}help for a list of commands")

        elif isinstance(exc, BadArgument):
            await ctx.reply(f"Bad argument, type {PREFIX}help for a list of commands")
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.reply("Argument(s) are missing from command")
        elif isinstance(exc, HTTPException):
            await ctx.reply("Unable to send message (likely too long)")
        elif isinstance(exc, Forbidden):
            await ctx.reply("I don't have permission to do that")
        elif isinstance(exc, MissingPermissions):
            await ctx.reply("You don't have permission to do that")
        else:
            await ctx.reply("Something went wrong (check logs)")
            raise exc

    async def on_ready(self):
        if not self.ready:
            # Daily birthday checker at noon est
            if USE_DB:
                self.scheduler.add_job(self.birthday_trigger, CronTrigger(second="0", minute="0", hour="12"))
                self.scheduler.start()

            self.ready = True
            print(get_current_time(), "Bot is ready")
            await self.change_presence(activity=discord.Game(f"{PREFIX}help"))
        else:
            print(get_current_time(), "Bot reconnected")

    # YOU NEED THIS FOR COMMANDS TO WORK
    async def on_message(self, message):
        cmdchannel = self.get_command_channel(message.guild.id)
        if cmdchannel and not message.author.bot:
            if message.channel.id == cmdchannel:
                await self.process_commands(message)
        else:
            if not message.author.bot:
                await self.process_commands(message)


bot = Bot()
