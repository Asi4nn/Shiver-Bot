from discord.ext.commands import Cog
from discord.ext.commands import command
import discord
# from discord.ext.commands import commands


class tests(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')
        print(f'Ping: {self.bot.letency * 1000}ms')

    @command(name="source")
    async def source(self, ctx):
        embed = discord.Embed(
            title='Shiver Discord Bot',
            description='Open source discord bot made for the chillzone discord',
            colour=discord.Colour.blue(),
            url='https://github.com/Leo-Wang-Toronto/Shiver-Bot'
        )

        embed.set_image(url='https://cdn.discordapp.com/attachments/452559141458935808/766780157708992562/snowflake2-2.jpg')
        embed.set_footer(text='Licensed under the MIT License')
        embed.add_field(name='Contributors:', value='From github.com/Leo-Wang-Toronto/Shiver-Bot')
        embed.add_field(name='Asi4n#4243', value='github.com/Leo-Wang-Toronto', inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(tests(bot))
