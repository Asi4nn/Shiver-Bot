from random import randint

from discord import Embed, Colour, File
from discord.errors import HTTPException
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import has_permissions

from lib.db import db_postgresql

# CONTRIBUTORS: add your discord tag and github link in this dictionary
CONTRIBUTORS = {
    "Asi4n#5622": "github.com/Asi4nn",
    "Epicsteve2": "github.com/Epicsteve2"
}


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
            await ctx.send(f"Set the announcement channel to {ctx.channel.name}")
        except:
            await ctx.send("Failed to set channel")


def setup(bot):
    bot.add_cog(General(bot))
