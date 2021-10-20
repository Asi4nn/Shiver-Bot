from typing import Optional

from discord import Embed
from discord.utils import get
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.menus import MenuPages, ListPageSource

from ..bot import PREFIX


def syntax(command):
    aliases = ", ".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

    params = " ".join(params)
    return f"```Aliases: {aliases} {params}```"


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=3)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(
            title=f"Help Menu ({PREFIX}help)",
            description="Descriptions of all commands in Shiver Bot!",
            colour=self.ctx.author.colour
        )

        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} of {len_data:,} commands.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []

        for entry in entries:
            fields.append((entry.brief or "No description", syntax(entry)))

        return await self.write_page(menu, fields)


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    @Cog.listener()
    async def on_ready(self):
        print("Help cog ready")

    async def cmd_help(self, ctx, command):
        embed = Embed(
            title=f"Info about {command} command",
            description=syntax(command),
            colour=ctx.author.colour
        )
        embed.add_field(name="Command description", value=command.brief)
        await ctx.send(embed=embed)

    @command(name="help", brief="Displays info about a command or all commands in Shiver Bot")
    async def show_help(self, ctx, cmd: Optional[str]):
        if cmd is None:
            menu = MenuPages(source=HelpMenu(ctx, list(self.bot.commands)), delete_message_after=True, timeout=60.0)
            await menu.start(ctx)
        else:
            command = get(self.bot.commands, name=cmd)
            if command is not None:
                await self.cmd_help(ctx, command)
            else:
                await ctx.send("That command doesn't exist")


def setup(bot):
    bot.add_cog(Help(bot))
