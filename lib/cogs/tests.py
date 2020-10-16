from discord.ext.commands import Cog
from discord.ext.commands import command
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
        await ctx.send('Shiver Bot was made by Asi4n#4243\nSource: github.com/Leo-Wang-Toronto/Shiver-Bot')

    @Cog.listener()
    async def on_ready(self):
        print("test cog ready")


def setup(bot):
    bot.add_cog(tests(bot))
