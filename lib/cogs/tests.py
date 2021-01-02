from random import randint
import re

from ..db import db
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import has_permissions
from discord.errors import HTTPException
from discord import Embed, Colour
from discord import Member

# CONTRIBUTORS: add your discord tag and github link in this dictionary
CONTRIBUTORS = {"Asi4n#5622": "github.com/Leo-Wang-Toronto"}


class tests(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        pass

    @command(name="ping", brief="Get the latency between the bot and the server")
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')

    @command(name="source", brief="Gets information about the bot with its contributors and repo")
    async def source(self, ctx):
        embed = Embed(
            title='Shiver Discord Bot',
            description='Open source discord bot made for the chillzone discord',
            colour=Colour.blue(),
            url='https://github.com/Leo-Wang-Toronto/Shiver-Bot'
        )

        embed.set_image(url='https://cdn.discordapp.com/attachments/452559141458935808/766780157708992562/snowflake2'
                            '-2.jpg')
        embed.set_footer(text='Licensed under the MIT License')
        embed.add_field(name='Contributors:', value='From github.com/Leo-Wang-Toronto/Shiver-Bot')
        for c in CONTRIBUTORS:
            embed.add_field(name=c, value=CONTRIBUTORS[c], inline=False)
        await ctx.send(embed=embed)

    @command(name="roll", aliases=['dice'], brief="Rolls some dice of your choice!")
    async def roll_dice(self, ctx, dice_type: str):
        dice, value = [int(v) for v in dice_type.lower().split("d")]
        if dice <= 0 or value <= 0:
            await ctx.send("You can't roll negative values dummy")
        elif dice > 100 or value > 100:
            await ctx.send("Values entered too large (over 100)")
        else:
            rolls = [randint(1, value) for i in range(dice)]
            await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

    @roll_dice.error
    async def roll_dice_error(self, ctx, exc):
        if isinstance(exc.original, HTTPException):
            await ctx.send("Result is too large D:")

    @command(name="at_everyone")
    async def at_everyone(self, ctx):
        await ctx.send("@everyone")

    @command(name="channel", brief="Set the channel for announcements")
    @has_permissions(manage_guild=True)
    async def channel(self, ctx):
        try:
            db.execute("INSERT OR REPLACE INTO channels(GuildID, channel) VALUES (?, ?)", ctx.guild.id, ctx.channel.id)
            await ctx.send(f"Set the announcement channel to {ctx.channel.name}")
        except:
            await ctx.send("Failed to set channel")


def setup(bot):
    bot.add_cog(tests(bot))
