from random import randint, choice
from re import fullmatch

from discord import Embed, Colour, File
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Cog, Context, command, check, has_permissions, has_guild_permissions

from lib.db import db_postgresql
from lib.bot import OWNER_IDS
from ..helpers.is_mention import is_mention

from time import sleep

# CONTRIBUTORS: add your discord tag and github link in this dictionary
CONTRIBUTORS = {
    "Asi4n#5622": "github.com/Asi4nn",
    "Epicsteve2": "github.com/Epicsteve2"
}


async def is_owner(ctx: Context):
    """Checks if the caller of the command is a bot owner"""
    return ctx.author.id in OWNER_IDS


class General(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("General cog ready")

    @command(name="ping", brief="Get the latency between the bot and the server")
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')

    @command(name="source", brief="Gets information about the bot with its contributors and repo")
    async def source(self, ctx):
        embed = Embed(
            title='Shiver Discord Bot',
            description='Open source discord bot made for small communities',
            colour=Colour.blue(),
            url='https://github.com/Asi4nn/Shiver-Bot'
        )

        image = open("data/images/snowflake2-2.jpg", "rb")
        file = File(image, filename="snowflake2-2.jpg")
        embed.set_image(url='attachment://snowflake2-2.jpg')
        embed.set_footer(text='Licensed under the MIT License')
        embed.add_field(name='Contributors:', value='https://github.com/Asi4nn/Shiver-Bot')
        for c in CONTRIBUTORS:
            embed.add_field(name=c, value=CONTRIBUTORS[c], inline=False)
        await ctx.send(embed=embed, file=file)
        image.close()

    @command(name="roll", aliases=['dice'], brief="Rolls some dice of your choice!")
    async def roll_dice(self, ctx, dice_type: str):
        if not fullmatch("\dd\d", dice_type):
            await ctx.send("Invalid dice format, (use ndm, where n is the number of dice and m is the number of faces")
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

    @command(name="channel", brief="Set the channel for announcements")
    @has_permissions(manage_guild=True)
    async def channel(self, ctx):
        try:
            db_postgresql.execute("INSERT INTO channels(GuildID, channel) "
                                  "VALUES (%s, %s) "
                                  "ON CONFLICT(GuildID) "
                                  "DO UPDATE SET channel = %s",
                                  ctx.guild.id, ctx.channel.id, ctx.channel.id)
            await ctx.send(f"Set the announcement channel to {ctx.channel.mention}")
        except:
            await ctx.send("Failed to set channel")

    @command(name="commandchannel", brief="Set the channel for commands, if this is not set, users can type "
                                          "commands anywhere")
    @has_permissions(manage_guild=True)
    async def commandchannel(self, ctx):
        try:
            db_postgresql.execute("INSERT INTO channels(GuildID, cmdchannel) "
                                  "VALUES (%s, %s) "
                                  "ON CONFLICT(GuildID) "
                                  "DO UPDATE SET cmdchannel = %s",
                                  ctx.guild.id, ctx.channel.id, ctx.channel.id)
            await ctx.send(f"Set the command channel to {ctx.channel.mention}")
        except:
            await ctx.send("Failed to set channel")

    @command(name="removecommandchannel", brief="Removes the command channel, if applicable")
    @has_permissions(manage_guild=True)
    async def removecommandchannel(self, ctx):
        try:
            db_postgresql.execute("INSERT INTO channels(GuildID, cmdchannel) "
                                  "VALUES (%s, NULL) "
                                  "ON CONFLICT(GuildID) "
                                  "DO UPDATE SET cmdchannel = NULL",
                                  ctx.guild.id)
            await ctx.send(f"Removed command channel")
        except:
            await ctx.send("Failed to set channel")

    # @check(is_owner)  # removing this would be a bad idea...
    @command(name="blend", brief="haha funny command")
    @has_guild_permissions(move_members=True)
    async def blend(self, ctx: Context, mention: str, amount="5"):
        if not amount.isdigit():
            await ctx.send("Enter a valid number to blend")
            return

        if is_mention(mention):
            member = ctx.guild.get_member(int(mention[3:len(mention) - 1]))
            if not member:
                await ctx.send("User not in guild...")
                return

            if member.bot:
                await ctx.send("Bots are immune to blending....")
                return

            if member.voice:
                await ctx.send(f"Blending {mention}")
                original_vc = member.voice.channel
                channels = ctx.guild.voice_channels
                channels.remove(original_vc)
                i = 0
                while i < int(amount):
                    try:
                        await member.move_to(channel=choice(channels))
                        sleep(0.5)
                        i += 1
                    except Forbidden:
                        pass

                await member.move_to(channel=original_vc)
            else:
                await ctx.send("User not in voice!")
        else:
            await ctx.send("Invalid mention!")


def setup(bot):
    bot.add_cog(General(bot))
