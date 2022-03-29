from random import randint, choice
from re import fullmatch

from discord import Embed, Colour, File
from discord import utils
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Cog, Context, command, has_permissions, has_guild_permissions

from lib.bot import OWNER_IDS, PREFIX
from lib.helpers.is_mention import is_mention
from lib.db import bot_queries

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

    @Cog.listener()
    async def on_guild_join(self, guild):
        general = utils.get(guild.text_channels, name="general")
        if general is not None:
            bot_queries.set_channel(general.id)

        await guild.text_channels[0].send("No general channel found! Set an announcement channel using "
                                          f"{PREFIX}channel")

    @command(name="ping", brief="Get the latency between the bot and the server")
    async def ping(self, ctx):
        await ctx.reply(f'Pong! {round(self.bot.latency * 1000)}ms')

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
        await ctx.reply(embed=embed, file=file)
        image.close()

    @command(name="roll", aliases=['dice'], brief="Rolls some dice of your choice!")
    async def roll_dice(self, ctx, dice_type: str):
        if not fullmatch(r"\dd\d", dice_type):
            await ctx.reply("Invalid dice format, (use ndm, where n is the number of dice and m is the number of faces")
        dice, value = [int(v) for v in dice_type.lower().split("d")]
        if dice <= 0 or value <= 0:
            await ctx.reply("You can't roll negative values dummy")
        elif dice > 100 or value > 100:
            await ctx.reply("Values entered too large (over 100)")
        else:
            rolls = [randint(1, value) for i in range(dice)]
            await ctx.reply(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

    @roll_dice.error
    async def roll_dice_error(self, ctx, exc):
        if isinstance(exc.original, HTTPException):
            await ctx.reply("Result is too large D:")

    @command(name="announcement_channel", aliases=["channel"], brief="Set the channel for announcements")
    @has_permissions(manage_guild=True)
    async def announcement_channel(self, ctx, channel):
        if (channel in [i.mention for i in ctx.guild.text_channels] and
                bot_queries.set_channel(ctx.guild.id, int(channel[2: len(channel) - 1]))):
            return await ctx.reply(f"Set the announcement channel to {channel}")
        await ctx.reply("Failed to set channel")

    @command(name="command_channel_set", aliases=["cmd_channel_set", "cmd_channel"],
             brief="Set the channel for commands, if this is not set, users can type commands anywhere")
    @has_permissions(manage_guild=True)
    async def command_channel_set(self, ctx, channel):
        if (channel in [i.mention for i in ctx.guild.text_channels] and
                bot_queries.set_command_channel(ctx.guild.id, int(channel[2: len(channel) - 1]))):
            return await ctx.reply(f"Set the command channel to {channel}")
        await ctx.reply("Failed to set channel")

    @command(name="command_channel_remove", aliases=["cmd_channel_rm"],
             brief="Removes the command channel, if applicable")
    @has_permissions(manage_guild=True)
    async def command_channel_remove(self, ctx):
        if bot_queries.remove_command_channel(ctx.guild.id):
            return await ctx.reply("Removed command channel")
        await ctx.reply("Failed to remove channel")

    # @check(is_owner)  # removing this would be a bad idea...
    @command(name="blend", brief="haha funny command")
    @has_guild_permissions(move_members=True)
    async def blend(self, ctx: Context, mention: str, amount="5"):
        if not amount.isdigit():
            await ctx.reply("Enter a valid number to blend")
            return

        if is_mention(mention):
            member = ctx.guild.get_member(int(mention[3:len(mention) - 1]))
            if not member:
                await ctx.reply("User not in guild...")
                return

            if member.bot:
                await ctx.reply("Bots are immune to blending....")
                return

            if member.voice:
                await ctx.reply(f"Blending {mention}")
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
                await ctx.reply("User not in voice!")
        else:
            await ctx.reply("Invalid mention!")


def setup(bot):
    bot.add_cog(General(bot))
