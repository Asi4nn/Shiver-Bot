import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from discord.ext.commands import Bot as BaseBot
from discord.ext.commands import when_mentioned_or
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, MissingPermissions, CheckFailure)
from discord.errors import HTTPException, Forbidden
from discord.utils import get

from ..helpers.getTime import get_current_time
from lib.db import db_postgresql as db

from os import listdir, environ
from os.path import sep

import re

TOKEN = environ['TOKEN']
PREFIX = '$'
OWNER_IDS = [164144088818515968]
COGS = []
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

for filename in listdir('./lib/cogs'):
    if filename.endswith('.py') and filename[:-3] != "log":     # disable message logging for saving db storage
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
        # with open(sep.join(["lib", "bot", "TOKEN.txt"]), 'r', encoding="utf-8") as token:
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
        await send_channel.send(f"@here Happy Birthday to {mention} who's turning {age} today!")

    def get_channel(self, guildID):
        return db.field("SELECT channel FROM channels WHERE GuildID = %s", guildID)

    def get_command_channel(self, guildID):
        return db.field("SELECT cmdchannel FROM channels WHERE GuildID = %s", guildID)

    async def birthday_trigger(self):
        bdays = db.records("SELECT UserID, date, GuildID FROM birthdays")

        for record in bdays:
            if int(bdays.date[0:2]) == datetime.today().day and int(bdays[3:5]) == datetime.today().month:
                channel = self.get_channel(record.GuildID)
                age = datetime.today().year - int(bdays[6:])
                await self.announce_birthday(record.GuildID, int(channel), f'<@!{record.UserID}>', age)

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
                await ctx.send(f"Command not found, type {PREFIX}help for a list of commands")
                
        elif isinstance(exc, BadArgument):
            await ctx.send(f"Bad argument, type {PREFIX}help for a list of commands")
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("Argument(s) are missing from command")
        elif isinstance(exc, HTTPException):
            await ctx.send("Unable to send message (likely too long)")
        elif isinstance(exc, Forbidden):
            await ctx.send("I don't have permission to do that")
        elif isinstance(exc, MissingPermissions):
            await ctx.send("You don't have permission to do that")
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            # Daily birthday checker
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
