from random import randint

from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.errors import HTTPException
from discord import Embed, Colour


class tests(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        pass

    @command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')

    @command(name="source")
    async def source(self, ctx):
        embed = Embed(
            title='Shiver Discord Bot',
            description='Open source discord bot made for the chillzone discord',
            colour=Colour.blue(),
            url='https://github.com/Leo-Wang-Toronto/Shiver-Bot'
        )

        embed.set_image(url='https://cdn.discordapp.com/attachments/452559141458935808/766780157708992562/snowflake2-2.jpg')
        embed.set_footer(text='Licensed under the MIT License')
        embed.add_field(name='Contributors:', value='From github.com/Leo-Wang-Toronto/Shiver-Bot')
        embed.add_field(name='Asi4n#4243', value='github.com/Leo-Wang-Toronto', inline=False)
        await ctx.send(embed=embed)

    @command(name="roll", aliases=['dice'])
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


def setup(bot):
    bot.add_cog(tests(bot))
